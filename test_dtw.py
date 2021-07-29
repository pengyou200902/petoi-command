import pyaudio
from my_dtw.utils_original import *


CHUNK = 512  # 每个缓冲区的帧数
FORMAT = pyaudio.paInt16  # 采样位数
CHANNELS = 1  # 单声道
RATE = 44100  # 采样频率

template = Voice(r'./my_dtw/recordings/1_1.wav')
me = Voice(r'./my_dtw/recordings/1_2.wav')

