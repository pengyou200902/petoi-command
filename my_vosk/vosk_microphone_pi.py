import os
import sys
import logging
import queue
# import numpy as np
import vosk
import sounddevice as sd
from common.cmd_lookup import text2cmd
from serialMaster import ardSerial


FORMAT = '%(asctime)-15s %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__name__)

device = sd.query_devices(kind='input')
device_name = device['name']
logger.info(device)
# device_index = device['index']

q = queue.Queue()


def load_model(model):
    """Load vosk model.

    Parameters
    ----------
    model : str, vosk.Model
        Getting an str means the function gets the path of vosk.Model. Getting a vosk.Model means the model has
        been loaded once so just return itself.

    Returns
    -------
    model : vosk.Model
        The loaded vosk model.

    Raises
    ------
    FileNotFoundError:
        An error occurs when model not exists in the path.

    ValueError:
        When getting an argument and it's not an instance of str OR vosk.Model.
    """

    if isinstance(model, str):
        if os.path.exists(model):
            model = vosk.Model(model)
            return model
        else:
            logger.info("Please download a model for your language from https://alphacephei.com/vosk/models")
            logger.info("and unpack as 'model' in the current folder.")
            raise FileNotFoundError('model not found, please correct the path.')
    elif isinstance(model, vosk.Model):
        return model
    else:
        raise ValueError('Unknown error while loading model.')


def callback(in_data, frames, time, status):
    """This is called (from a separate thread) for each audio block.

    Parameters
    ----------
    in_data : _cffi_backend.buffer
        The audio stream chunk.

    frames : int
        The size of in_data.

    time : _cffi_backend._CDataBase
        Time info.

    status : sounddevice.CallbackFlags
        Indicates whether there's an error during reading audio stream.
    """

    # print(type(in_data), in_data)
    # print(type(frames), frames)
    # print(type(time), time)
    # print(type(status), status)
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(in_data))
    # print()


def action_listen(ser, model, sample_rate, cmd_table, d, chunk):
    """The function to receive and recognize voice commands. And then excecute the corresponding Petoi command.

    Parameters
    ----------
    ser : serial.Serial
        The serial port of Petoi.

    model : vosk.Model
        The loaded vosk model for speech recognition.

    sample_rate : int
        The sample rate when receiving audio data.

    cmd_table : dict{ str:str }
        Key represents the result of speech recognition(voice command).
        Value represents the corresponding Petoi command.

    d : str
        A customized dictionary indicating the range of words to be recognized.

    chunk : int
        The chunk size of the audio stream data.

    Returns
    -------
    cmd : str
        The corresponding Petoi command that is finally executed.

    Raises
    ------
    Exception:
        In case that the program may encounter an exception.
    """

    if sample_rate is None:
        # Get the default audio input device of your system.
        device_info = sd.query_devices(device, 'input')
        # soundfile expects an int, sounddevice provides a float.
        sample_rate = int(device_info['default_sample_rate'])

    try:
        # The 3rd argument(can be omitted) is a custom dictionary including all candidate words/characters.
        rec = vosk.KaldiRecognizer(model, sample_rate, d)
        # Open a stream and read real-time audio stream data.
        with sd.RawInputStream(samplerate=sample_rate, blocksize=chunk * 10, device=device_name, dtype='int16',
                               channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            while True:
                data = q.get()
                # Send the received audio data into recognizer
                if rec.AcceptWaveform(data):
                    res = rec.Result()
                    # The structure of res is fixed, so for convenience
                    text = res[14:-3]

                    print(f'final text: {text}')
                    # Get the mapped Petoi command.
                    cmd = text2cmd(text, cmd_table)
                    if cmd:
                        if ser:
                            # Execute the command if there exists a serial port.
                            ardSerial.execute(ser, cmd)
                        logger.info(f'exec command: {cmd}')
                        return cmd
                else:
                    # When the recognizer thinks the audio data is not a complete sentence.
                    partial = rec.PartialResult()
                    # print(type(partial), partial==p)
                    if not partial[16] == partial[17] == '"':
                        logger.debug(f'partial: {partial}')
    # In case that the program encounters an exception.
    except Exception as e:
        if ser:
            ardSerial.execute(ser, 'd\n')
            ardSerial.close_serial(ser)
        raise e
