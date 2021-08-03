# coding=utf-8
import os
import subprocess
import time
import threading
import librosa
import numpy as np
import soundfile as sf
import sounddevice as sd
from collections import deque
from dtw import dtw
import logging

LOG_FORMAT = '%(asctime)-15s %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

DEVICE = sd.query_devices(kind='input')
DEVICE_NAME = DEVICE['name']

CHUNK = 4000  # 每个缓冲区的帧数
RATE = 16000  # 采样频率
CHUNK_TIME = 1 / RATE * CHUNK
CHANNELS = 1  # 单声道
audio_path = r'./recordings/'


def euclidean_distance(vec_1, vec_2):
    return np.linalg.norm(vec_1 - vec_2)


def get_path():
    cur_dir = os.getcwd()
    new_path = 'recordings'
    cur_dir = cur_dir + '/' + new_path
    if os.path.exists(cur_dir):
        pass
    else:
        os.mkdir(cur_dir)
    return cur_dir


def resample(src, dst, n_channels=CHANNELS, rate=RATE):
    cmd = 'ffmpeg -y -i %s -ar %d -ac %d -sample_fmt s16 %s' % (src, rate, n_channels, dst)
    try:
        ret = subprocess.run(cmd, shell=True, encoding='utf-8', check=True)
    except Exception as e:
        raise e
    else:
        return ret.returncode == 0  # success


# audio point check
def strip_silence(wave_data, frame_length=CHUNK, hop_length=CHUNK // 2):
    energies = librosa.feature.rms(y=wave_data, frame_length=frame_length, hop_length=hop_length)[0]
    thresh = 1 * np.median(energies)
    # thresh = 0.618 * np.median(energies)
    keep_index = np.where(energies > thresh)
    new_signal_index = librosa.frames_to_samples(keep_index, hop_length=hop_length)[0]
    if len(new_signal_index) > 1:
        new_signal = np.concatenate([wave_data[x: x + hop_length] for x in new_signal_index if x < len(wave_data)])
    else:
        return np.zeros_like(wave_data)
        # new_signal = wave_data[new_signal_index[0]: new_signal_index[0] + hop_length]

    return new_signal


def convert_strip(frames: [list, deque], frame_length=CHUNK, hop_length=CHUNK // 2):
    data = b''.join(frames)
    data = np.frombuffer(data, np.int16) / 2 ** 15
    data = strip_silence(data, frame_length, hop_length)
    # data = data.astype(np.int16)
    return data


def get_start_id():
    folder = get_path()
    content = os.listdir(folder)
    return len(content)


def get_audio_files(audio_path=audio_path, endswith='.wav'):
    templates = [
        x for x in os.listdir(audio_path) if x.endswith(endswith) or x.endswith(endswith.upper())
    ]
    return sorted(templates)


# Not used
def find_closest(voice: 'Voice', template_voices: list, need_strip=False):
    score = float('inf')
    closest_voice = None
    # templates = get_audio_files(audio_path, '.wav')

    for t in template_voices:
        # full_path = os.path.join(audio_path, t)
        try:
            # v = Voice(file_path=t)
            s = t.dtw_with(another=voice)
        except Exception as e:
            logger.error(e)  # logging will be used in the future
        else:

            if s.normalizedDistance < score:
                score = s.normalizedDistance
                closest_voice = t

    return score, closest_voice


class Listener:
    def __init__(self, template: 'Voice', chunk=CHUNK, n_channels=CHANNELS, rate=RATE):
        self.chunk = chunk
        self.channels = n_channels
        self.rate = rate
        self.window_size = int(2 / CHUNK_TIME)
        self.template = template
        self.thresh = 0  # For finding proper threshold.
        # self.thresh = 70  # For Mac
        # self.thresh = 50 # For Pi

        self._wakeup = False
        self._running = False
        self._frame_window = deque([], maxlen=self.window_size)
        self._frames = deque([], maxlen=int(5 / CHUNK_TIME))
        print(f'Listener唤醒词使用模板：{self.template.file_path}')

    def listening(self):
        result = ''
        self._wakeup = False
        stream = sd.RawInputStream(samplerate=self.rate, device=DEVICE_NAME, blocksize=self.chunk,
                                   channels=1, dtype='int16')
        stream.start()

        while not self._wakeup:
            data = stream.read(self.chunk)
            self._frames.append(data[0])

            if len(self._frames) > self.window_size:
                # print('start')
                if self._frame_window:
                    self._frame_window.popleft()
                    self._frame_window.popleft()
                    self._frame_window.popleft()
                    self._frame_window.popleft()
                    self._frame_window.append(self._frames.popleft())
                    self._frame_window.append(self._frames.popleft())
                    self._frame_window.append(self._frames.popleft())
                    self._frame_window.append(self._frames.popleft())
                else:
                    # when sliding window is not full and there are existing cached frames,
                    # add the cached frames into the sliding window.
                    while len(self._frame_window) < self.window_size and len(self._frames) > 0:
                        self._frame_window.append(self._frames.popleft())
                signal = convert_strip(self._frame_window, self.chunk, self.chunk // 2)
                # for now signal is a float ndarray
                v = Voice(signal)
                s = time.time()
                result = v.dtw_with(self.template)
                logger.debug(f'len(_frames)={len(self._frames)}, DTW time cost: {time.time()-s}s, '
                             f'DTW.normalizedDistance={result.normalizedDistance}')
                if result.normalizedDistance < self.thresh:
                    logger.info('唤醒')
                    self.wakeup()
                    self._frames.clear()
                    self._frame_window.clear()

        stream.stop()
        stream.close()
        logger.info("结束监听")
        return result

    def wakeup(self):
        self._wakeup = True

    def is_wakeup(self):
        return self._wakeup

    def reset(self, wakeup=False):
        self._wakeup = wakeup
        self._frames.clear()
        self._frame_window.clear()


class Recorder:
    def __init__(self, chunk=CHUNK, n_channels=CHANNELS, rate=RATE):
        self.chunk = chunk
        self.channels = n_channels
        self.rate = rate
        self._running = True
        self._frames = []

    def start(self):
        threading.Thread(target=self.__recording).start()

    def __recording(self):
        self._running = True
        self._frames.clear()

        stream = sd.RawInputStream(samplerate=self.rate, device=DEVICE_NAME, blocksize=self.chunk,
                                   channels=1, dtype='int16')
        stream.start()

        while self._running:
            data = stream.read(self.chunk)
            # data[0] is _cffi_backend.buffer object
            self._frames.append(data[0])

        stream.stop()
        stream.close()

    def stop(self):
        self._running = False

    def save(self, filename, mode='x'):
        if not filename.endswith(".wav"):
            filename = filename + ".wav"
        path = get_path()
        raw = path + r'/raw_' + filename
        filename = path + r'/' + filename
        # save raw audio
        with sf.SoundFile(raw, mode=mode, samplerate=self.rate,
                          channels=1, subtype=sf.default_subtype('wav')) as file:
            data = b''.join(self._frames)
            data = np.frombuffer(data, np.int16)
            file.write(data)
        # save audio after strip
        with sf.SoundFile(filename, mode=mode, samplerate=self.rate,
                          channels=1, subtype=sf.default_subtype('wav')) as file:
            data = convert_strip(self._frames, self.chunk, self.chunk // 2)
            data = data * 2**15
            data = data.astype(np.int16)
            file.write(data)
        return filename, raw

    def record(self):
        a = input('请输入数字【2】并回车【开始】录音：\n')
        if a == '2':
            begin = time.time()
            logger.debug("开始录音")
            self.start()
            b = input('请输入数字【2】并回车【结束】录音：\n')
            if b == '2':
                logger.debug("停止录音")
                self.stop()
                end = time.time()
                t = end - begin
                print(f'录音时间为{t}s')

    def run(self):
        i = 0
        num = 1  # num is used when saving file
        count = self.get_count()
        if count == 0:
            logger.debug('跳过录音')
            return None
        logger.debug('开始录制')
        print("请说话，比如说'嘿，Bittle'")
        while i < count:
            mode = 'x'
            self.record()
            # 录音循环
            while True:
                print('【本条重录】请输入【y】然后回车，【保存此条并继续】请输入【s】然后回车：')
                answer = input()
                if answer.upper() == 'Y':
                    mode = 'w'
                    self.record()
                else:
                    i += 1
                    break
            # 文件名循环
            while True:
                filename = "template_%d.wav" % num
                try:
                    raw, filename = self.save(filename, mode)
                except OSError:
                    logger.warning(f'文件（名）{filename} 已存在，程序将自动更换。')
                    num += 1
                else:
                    num += 1
                    print(f'录音保存在：{filename}')
                    yield raw, filename
                    break

    def get_count(self):
        count = input('请输入录制样本数（测试阶段，建议输入1录制1条方便调试，输入数字 0 跳过）：\n')
        try:
            count = int(count)
        except ValueError as e:
            print('无效输入，跳过录音。')
            return 0
        else:
            if count > 1:
                print('可以输入大于1，这将录制多条语音')
            return count


class Voice:
    def __init__(self, path_or_data):
        if isinstance(path_or_data, str):
            self.file_path = None
            self.mfcc = None
            self.__load_data(path_or_data)
        elif isinstance(path_or_data, (list, np.ndarray, bytes)):
            logger.debug("Voice's constructor got audio data")
            self.file_path = None
            self.mfcc = None
            self.wave_data = path_or_data
            self.sample_rate = RATE

    def __load_data(self, file_path):
        try:
            self.wave_data, self.sample_rate = librosa.load(file_path, sr=RATE)
            self.n_frames = len(self.wave_data)
            self.file_path = file_path
            self.name = os.path.basename(file_path)  # 记录下文件名
            return True
        except Exception as e:
            raise e

    def dtw_with(self, another: 'Voice'):
        return dtw(another.get_mfcc().T, self.get_mfcc().T, dist_method='euclidean')

    def get_mfcc(self):
        if self.mfcc is None:
            self.mfcc = librosa.feature.mfcc(y=self.wave_data, sr=self.sample_rate, n_mfcc=20)
        return self.mfcc

    def play(self):
        # sounddevice needs int16 while librosa uses float
        data = self.wave_data * 2**15
        data = data.astype(np.int16)
        sd.play(data, self.sample_rate)
        sd.wait()


# lis = Listener()
# lis.run()
# print('-' * 50)

# recorder = Recorder()
# a = list(recorder.run())
# print(a)

# v = Voice(r'./recordings/template.wav')
# v.play()

# print(get_path())
