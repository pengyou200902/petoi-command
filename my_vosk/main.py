import logging
import utils
from importlib import import_module
from serialMaster import ardSerial
from serial.serialutil import SerialException
from vosk_microphone_pi import action_listen, load_model

FORMAT = '%(asctime)-15s %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__name__)

# port='/dev/cu.BittleSPP-3534C8-Port'
# port='/dev/ttyS0'  # needed when using Pi
port = '/dev/cu.wchusbserial1430'  # needed when using Mac


def load_config(path: str = './config/config.yml'):
    import yaml
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        # print(config)
    except FileNotFoundError as e:
        logger.error(f'config file not exists: {path}')
        raise e
    else:
        return config


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


def task_listen(ser, listener):
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
        if ser:
            # Execute the command if there exists a serial port.
            ardSerial.execute(ser, 'm0 -40')
            ardSerial.execute(ser, 'm0 0')
        logger.info('end')
        listener.reset()
        return result


def task_action(ser, model, sample_rate, cmd_table, d, chunk):
    """The function for receiving, recognizing and executing the voice commands.

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
    """

    logger.info("开始act")
    action_listen(ser=ser, model=model, sample_rate=sample_rate, cmd_table=cmd_table, d=d, chunk=chunk)


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

    table_pkg = import_module(configs['cmd_table']['package'])
    cmd_table = getattr(table_pkg, configs['cmd_table']['table_name'])
    build_dict = getattr(table_pkg, configs['cmd_table']['build_dict'])

    # Chunk size of audio stream data for vosk recognizer.
    vosk_chunk = 20
    # The rate of audio stream data for vosk recognizer.
    sample_rate = 16000

    # If there's no specific template
    if not configs['Listener']['template']:
        # First you should record the template audio for wakeup word,but you can choose to skip.
        recorder = utils.Recorder(folder=configs['recording_path'])
        task_record(recorder=recorder)

        # Ask for your choice
        template_path = select_template(template_folder=configs['recording_path'])
        # Load the selected template wav file as a Voice object.
        template = utils.Voice(template_path)
    else:
        template = utils.Voice(configs['Listener']['template'])
    # Initialize the Listener of wakeup word.
    listener = utils.Listener(template=template, thresh=configs['Listener']['thresh'])

    # Initialize vosk model for speech recognition.
    d = build_dict(cmd_table)
    model = load_model(model=configs['vosk_model_path'])

    while True:
        if mode == 0:
            logger.debug(f'mode={mode}, task_listen')
            if task_listen(ser, listener=listener):
                mode = 1

        elif mode == 1:
            logger.debug(f'mode={mode}, action_listen')
            task_action(ser=ser, model=model, sample_rate=sample_rate, cmd_table=cmd_table, d=d, chunk=vosk_chunk)
            mode = 0


configs = load_config('./config/config.yml')

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
