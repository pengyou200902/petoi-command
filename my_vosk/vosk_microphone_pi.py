import os
import sys
import logging
import threading
import queue
import sounddevice as sd
import vosk
import utils
from cmd_lookup import text2cmd, build_dict
from serialMaster import ardSerial


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
sem = threading.Semaphore()


def load_model(model):
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
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(in_data))


def action_listen(ser, model, sample_rate, d, chunk):
    if sample_rate is None:
        device_info = sd.query_devices(device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        sample_rate = int(device_info['default_sample_rate'])

    try:
        # The 3rd argument(can be omitted) is a custom dictionary including all candidate words/characters.
        rec = vosk.KaldiRecognizer(model, sample_rate, d)

        with sd.RawInputStream(samplerate=sample_rate, blocksize=chunk*10, device=device_name, dtype='int16',
                               channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    res = rec.Result()
                    # The structure of res is fixed, so
                    text = res[14:-3]  # for English
                    # text = res[14:-3].replace(' ', '')  # for Chinese

                    print(f'final text: {text}')
                    cmd = text2cmd(text)
                    if cmd:
                        ardSerial.execute(ser, cmd)
                        logger.info(f'exec command: {cmd}')
                        return cmd
                else:
                    partial = rec.PartialResult()
                    # print(type(partial), partial==p)
                    if not partial[16] == partial[17] == '"':
                        logger.debug(f'partial: {partial}')

    except Exception as e:
        ardSerial.execute(ser, 'd\n')
        ardSerial.close_serial(ser)
        raise e


def task_record(recorder):
    files = list(recorder.run())
    print('-' * 50)
    return files


def task_listen(listener):
    logger.info('listen开始监听')
    result = listener.listening()
    if listener.is_wakeup():
        logger.info('end')
        listener.reset(wakeup=False)
        return result


def task_action(ser, model, sample_rate, d, chunk):
    logger.info("开始act")
    action_listen(ser=ser, model=model, sample_rate=sample_rate, d=d, chunk=chunk)


def main_loop(mode=0):
    vosk_chunk = 20
    sample_rate = 16000

    # First you should record the template audio for wakeup word. You can choose to skip.
    recorder = utils.Recorder()
    recordings = task_record(recorder=recorder)
    if not recordings or not os.path.exists(recordings[0][0]):
        # This is the default path for your template wav file of wakeup keyword.
        # If you skip recording, please make sure you have a template file.
        template_path = r'./recordings/template_1.wav'
    else:
        # Once you choose to record a new template, even if you record multiple templates,
        # the program will always choose the first one. You can change the logic.
        template_path = recordings[0][0]
    template = utils.Voice(template_path)

    # Initialize the Listener of wakeup word.
    listener = utils.Listener(template=template)

    # Initialize vosk model for speech recognition
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


ser = ardSerial.get_serial(port=port)
ardSerial.open_serial(ser)
try:
    main_loop(mode=0)

except KeyboardInterrupt:
    print('\nDone, exit')
    ardSerial.execute(ser, 'd\n')
    ardSerial.close_serial(ser)
    exit(0)
