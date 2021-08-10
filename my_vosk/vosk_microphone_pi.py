import os
import sys
import logging
import threading
import queue

import numpy as np
import sounddevice as sd
import vosk
import utils
from common.cmd_lookup import text2cmd, build_dict
from serialMaster import ardSerial
from serial.serialutil import SerialException

FORMAT = '%(asctime)-15s %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__name__)

default_model = r'./models/model'
device = sd.query_devices(kind='input')
device_name = device['name']
logger.info(device)
# device_index = device['index']

# port='/dev/cu.BittleSPP-3534C8-Port'
# port='/dev/ttyS0'  # needed when using Pi
port = '/dev/cu.wchusbserial1430'  # needed when using Mac
q = queue.Queue()


def load_model(model):
    """Load vosk model.

    Parameters
    ----------
    model : str OR vosk.model
        Getting an str means the function gets the path of vosk.model. Getting a vosk.model means the model has
        been loaded once so just return itself.

    Returns
    -------
    model : vosk.model
        The loaded vosk model.

    Raises
    ------
    FileNotFoundError:
        An error occurs when model not exists in the path.

    ValueError:
        When getting an argument and it's not an instance of str OR vosk.model.
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


def action_listen(ser, model, sample_rate, d, chunk):
    """The function to receive and recognize voice commands. And then excecute the corresponding Petoi command.

    Parameters
    ----------
    ser : serial.Serial
        The serial port of Petoi.

    model : vosk.model
        The loaded vosk model for speech recognition.

    sample_rate : int
        The sample rate when receiving audio data.

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
                    text = res[14:-3]  # for English
                    # text = res[14:-3].replace(' ', '')  # for Chinese

                    print(f'final text: {text}')
                    # Get the mapped Petoi command.
                    cmd = text2cmd(text)
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


def task_record(recorder):
    """The function for recording templates.

    Parameters
    ----------
    recorder : utils.Recorder
        An instance of utils.Recorder that can record multiple template recordings.
    """

    files = list(recorder.run())
    print('-' * 50)
    return files


def task_listen(listener):
    """The function for listening to the wakeup word.

    Parameters
    ----------
    listener : utils.Listener
        An instance of utils.Listener that can record (multiple) template recordings.

    Returns
    -------
    result : dtw.DTW
        An instance of dtw.DTW. The result of dtw(distance) calculation.
    """

    logger.info('listen开始监听')
    result = listener.listening()
    if listener.is_wakeup():
        logger.info('end')
        listener.reset()
        return result


def task_action(ser, model, sample_rate, d, chunk):
    """The function for receiving, recognizing and executing the voice commands.

    Parameters
    ----------
    ser : serial.Serial
        The serial port of Petoi.

    model : vosk.model
        The loaded vosk model for speech recognition.

    sample_rate : int
        The sample rate when receiving audio data.

    d : str
        A customized dictionary indicating the range of words to be recognized.

    chunk : int
        The chunk size of the audio stream data.
    """

    logger.info("开始act")
    action_listen(ser=ser, model=model, sample_rate=sample_rate, d=d, chunk=chunk)


def select_template(template_folder: str = r'./recordings'):
    """The function that asks users to choose a template wav file for wakeup word recognition.

    Parameters
    ----------
    template_folder : str
        The path of the folder that contains all the recordings.

    Returns
    -------
    template : str
        The path to the template wav file.
    """

    recordings = utils.get_audio_files(audio_path=template_folder, endswith='.wav')
    print('用【数字编号】选择要使用的录音作为模板：')
    for i, r in enumerate(recordings):
        print(f'\t{i}. {r}')
    c = input('你的选择 >>> ')
    try:
        c = int(c)
    except (ValueError, IndexError) as e:
        # This is the default path for your template wav file of wakeup keyword.
        # If you skip recording, please make sure you have a template file.
        template = template_folder + '/' + 'template_1.wav'
        print('无效输入，默认选择 template_1.wav')
    else:
        template = template_folder + '/' + recordings[c]
    return template


def main_loop(mode=0):
    """The loop for waking up Petoi and sending voice commands.

    Parameters
    ----------
    mode : int
        0 if you want to begin with wakeup recognition.
        1 if you want to begin with command recognition.
    """

    # Chunk size of audio stream data for vosk recognizer.
    vosk_chunk = 20
    # The rate of audio stream data for vosk recognizer.
    sample_rate = 16000

    # First you should record the template audio for wakeup word,but you can choose to skip.
    recorder = utils.Recorder()
    task_record(recorder=recorder)
    template_path = select_template(r'./recordings')
    # Load the chosen template wav file as a Voice object.
    template = utils.Voice(template_path)

    # Initialize the Listener of wakeup word.
    listener = utils.Listener(template=template)

    # Initialize vosk model for speech recognition.
    d = build_dict()
    model = load_model(model=default_model)

    while True:
        if mode == 0:
            logger.debug(f'mode={mode}, task_listen')
            if task_listen(listener=listener):
                mode = 1

        elif mode == 1:
            logger.debug(f'mode={mode}, action_listen')
            task_action(ser=ser, model=model, sample_rate=sample_rate, d=d, chunk=vosk_chunk)
            mode = 0


try:
    ser = ardSerial.get_serial(port=port)
except SerialException as e:
    ser = None
    logger.warning(f'Not able to get the serial port. Program will continue, but will not actually send the command.')
else:
    logger.debug(f'Got serial port.')
    ardSerial.open_serial(ser)

try:
    main_loop(mode=0)
except KeyboardInterrupt:
    print('\nDone, exit')
    if ser:
        ardSerial.execute(ser, 'd\n')
        ardSerial.close_serial(ser)
    exit(0)
