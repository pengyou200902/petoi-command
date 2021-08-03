# coding=utf-8
import os
import subprocess
import time
import threading
import wave
import pyaudio
import librosa
import numpy as np

from collections import deque
from dtw import dtw
from scipy.io import wavfile

import logging
FORMAT = '%(asctime)-15s %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__name__)

CHUNK = 4000  # 每个缓冲区的帧数
RATE = 16000  # 采样频率
chunk_time = 1 / RATE * CHUNK
CHANNELS = 1  # 单声道
FORMAT = pyaudio.paInt16  # 采样位数，16 bit int

audio_path = r'../recordings/'


def euclidean_distance(vec_1, vec_2):
    return np.linalg.norm(vec_1 - vec_2)


def get_path():
    cur_dir = os.getcwd()
    new_path = '../recordings'
    cur_dir = cur_dir + '/' + new_path
    if os.path.exists(cur_dir):
        pass
    else:
        os.mkdir(cur_dir)
    return cur_dir


def resample(src, dst, n_channels=CHANNELS, rate=RATE, format=FORMAT):
    cmd = 'ffmpeg -y -i %s -ar %d -ac %d -sample_fmt s16 %s' % (src, RATE, CHANNELS, dst)
    try:
        ret = subprocess.run(cmd, shell=True, encoding='utf-8', check=True)
    except Exception as e:
        raise e
    else:
        return ret.returncode == 0  # success


# audio point check
def strip_silence(wave_data, frame_length=CHUNK, hop_length=CHUNK // 2):
    energies = librosa.feature.rms(y=wave_data, frame_length=frame_length, hop_length=hop_length)[0]
    # thresh = 1 * np.median(energies)
    thresh = 0.618 * np.median(energies)
    keep_index = np.where(energies > thresh)
    new_signal_index = librosa.frames_to_samples(keep_index, hop_length=hop_length)[0]
    if len(new_signal_index) > 1:
        new_signal = np.concatenate([wave_data[x: x + hop_length] for x in new_signal_index if x < len(wave_data)])
    else:
        return np.zeros(wave_data)
        # new_signal = wave_data[new_signal_index[0]: new_signal_index[0] + hop_length]

    return new_signal


def convert_strip(frames: [list, deque], frame_length=CHUNK, hop_length=CHUNK // 2):
    data = b''.join(frames)
    data = np.frombuffer(data, np.int16) / 2 ** 15
    data = strip_silence(data, frame_length, hop_length)
    # data = data.astype(np.int16)
    return data


def save_for_pyaudio(wave_data, filepath, rate=RATE):
    try:
        wave_data *= 2 ** 15  # Same as wave_data *= 2<<14, this is for PyAudio to be able to play this file
        wavfile.write(filepath, rate, wave_data.astype(np.int16))
    except Exception as e:
        raise e
    else:
        return True


def get_start_id():
    folder = get_path()
    content = os.listdir(folder)
    return len(content)


def get_audio_files(audio_path=audio_path, endswith='.wav'):
    templates = [
        x for x in os.listdir(audio_path) if x.endswith(endswith) or x.endswith(endswith.upper())
    ]
    return sorted(templates)


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
    def __init__(self, chunk=CHUNK, n_channels=CHANNELS, rate=RATE, sample_format=FORMAT):
        self.CHUNK = chunk
        self.FORMAT = sample_format
        self.CHANNELS = n_channels
        self.RATE = rate
        self.window_size = int(2 / chunk_time)
        self.thresh = 70

        self._wakeup = False
        self._running = False
        self._frame_window = deque([], maxlen=self.window_size)
        self._frames = deque([], maxlen=int(5 / chunk_time))

    def start(self):
        threading.Thread(target=self.listening).start()

    def listening(self):
        result = ''
        template = Voice(r'./recordings/template.wav')
        # self._wakeup = False
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        while not self._wakeup:
            data = stream.read(self.CHUNK)
            self._frames.append(data)
            # print()
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
                    while len(self._frame_window) < self.window_size\
                            and len(self._frames) > 0:
                        self._frame_window.append(self._frames.popleft())
                signal = convert_strip(self._frame_window, self.CHUNK, self.CHUNK // 2)
                # for now signal is a float ndarray
                v = Voice(signal)
                s = time.time()
                result = v.dtw_with(template)
                logger.info(f'dtw cost {time.time()-s} s')
                logger.info(f'{len(self._frames)}, {result.normalizedDistance}')
                if result.normalizedDistance < self.thresh:
                    logger.info('唤醒')
                    self.wakeup()
                    self._frames.clear()
                    self._frame_window.clear()

        stream.stop_stream()
        stream.close()
        p.terminate()
        logger.info("结束监听")
        return result

    def wakeup(self):
        self._wakeup = True

    def is_wakeup(self):
        return self._wakeup

    def reset(self, running=False, wakeup=False):
        self._running = running
        self._wakeup = wakeup
        self._frames.clear()
        self._frame_window.clear()

    def stop(self):
        self._running = False

    def is_running(self):
        return self._running


class Recorder:
    def __init__(self, chunk=CHUNK, n_channels=CHANNELS, rate=RATE, sample_format=FORMAT):
        self.CHUNK = chunk
        self.FORMAT = sample_format
        self.CHANNELS = n_channels
        self.RATE = rate
        self._running = True
        self._frames = []

    def start(self):
        threading.Thread(target=self.__recording).start()

    def __recording(self):
        self._running = True
        self._frames = []
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        while self._running:
            data = stream.read(self.CHUNK)
            self._frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self._running = False

    def save(self, filename):
        p = pyaudio.PyAudio()

        if not filename.endswith(".wav"):
            filename = filename + ".wav"
        path = get_path()

        filename = path + r'//' + filename

        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()
        print("录音已保存")

    def record(self):
        print('请输入数字2并回车开始录音：')
        a = input()
        if a == '2':
            begin = time.time()
            logger.info("Start recording")
            self.start()
            print('请输入数字2并回车结束录音：')
            b = input()
            if b == '2':
                logger.info("Stop recording")
                self.stop()
                end = time.time()
                t = end - begin
                print(f'录音时间为{t}s')

    def run(self):
        count = 0
        i = count + 2
        m = self.get_count()
        if m == 0:
            logger.info('跳过录音')
            return
        logger.info('开始录制')
        print("比如说'嘿，Bittle'")
        self.record()
        self.save("1_1.wav")
        while i < (m + count + 1):
            print('继续录音请输入数字2并回车，本条重录请输入y or Y：')
            answer = input()
            if answer.upper() == 'Y':
                count += 1
                self.record()
                self.save("1_%d.wav" % (i - count))
                i += 1
            else:
                self.record()
                self.save("1_%d.wav" % (i - count))
                i += 1

    def get_count(self):
        count = input('请输入录制样本数（输入数字 0 跳过）：')
        try:
            count = int(count)
        except ValueError as e:
            return 0
        else:
            return count


class Voice:
    def __init__(self, path_or_data):
        if isinstance(path_or_data, str):
            self.file_path = None
            self.mfcc = None
            self.__load_data(path_or_data)
        elif isinstance(path_or_data, (list, np.ndarray, bytes)):
            logger.info("Constructor got audio data")
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

    def play(self):  # wrong implementation
        chunk = CHUNK
        wf = wave.open(self.file_path, 'rb')
        p = pyaudio.PyAudio()
        # 播放音乐
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        while True:
            data = wf.readframes(chunk)
            if data == "":
                break
            stream.write(data)
        stream.close()
        p.terminate()




# lis = Listener()
# lis.run()
# print('-' * 50)


# v = Voice(r'./recordings/1_1.wav')
# Voice.play(v.file_path)