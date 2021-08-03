import sounddevice as sd
import soundfile as sf
import numpy as np

device = sd.query_devices(kind='input')
device_name = device['name']
device_index = sd.default.device[0]


# device_info = sd.query_devices(kind='input')
# soundfile expects an int, sounddevice provides a float:
samplerate = 16000
chunk = 400
filename = r'./sd.wav'

try:
    with sf.SoundFile(filename, mode='w', samplerate=samplerate,
                      channels=1, subtype='PCM_16') as file:
        stream = sd.RawInputStream(samplerate=samplerate, device=device_name, blocksize=chunk,
                                   channels=1, dtype='int16')
        print('#' * 80)
        print('press Ctrl+C to stop the recording')
        print('#' * 80)
        stream.start()
        while True:
            data = stream.read(chunk)
            print(type(data[0]))
            data = np.frombuffer(data[0], np.int16)
            file.write(data)
except KeyboardInterrupt:
    stream.close()
    print('\nRecording finished: ' + repr(filename))
    exit(0)
except Exception as e:
    stream.close()
    raise e
    # exit(type(e).__name__ + ': ' + str(e))


# _formats = {
#     'WAV':   0x010000,  # Microsoft WAV format (little endian default).
#     'AIFF':  0x020000,  # Apple/SGI AIFF format (big endian).
#     'AU':    0x030000,  # Sun/NeXT AU format (big endian).
#     'RAW':   0x040000,  # RAW PCM data.
#     'PAF':   0x050000,  # Ensoniq PARIS file format.
#     'SVX':   0x060000,  # Amiga IFF / SVX8 / SV16 format.
#     'NIST':  0x070000,  # Sphere NIST format.
#     'VOC':   0x080000,  # VOC files.
#     'IRCAM': 0x0A0000,  # Berkeley/IRCAM/CARL
#     'W64':   0x0B0000,  # Sonic Foundry's 64 bit RIFF/WAV
#     'MAT4':  0x0C0000,  # Matlab (tm) V4.2 / GNU Octave 2.0
#     'MAT5':  0x0D0000,  # Matlab (tm) V5.0 / GNU Octave 2.1
#     'PVF':   0x0E0000,  # Portable Voice Format
#     'XI':    0x0F0000,  # Fasttracker 2 Extended Instrument
#     'HTK':   0x100000,  # HMM Tool Kit format
#     'SDS':   0x110000,  # Midi Sample Dump Standard
#     'AVR':   0x120000,  # Audio Visual Research
#     'WAVEX': 0x130000,  # MS WAVE with WAVEFORMATEX
#     'SD2':   0x160000,  # Sound Designer 2
#     'FLAC':  0x170000,  # FLAC lossless file format
#     'CAF':   0x180000,  # Core Audio File format
#     'WVE':   0x190000,  # Psion WVE format
#     'OGG':   0x200000,  # Xiph OGG container
#     'MPC2K': 0x210000,  # Akai MPC 2000 sampler
#     'RF64':  0x220000,  # RF64 WAV file
# }
#
# _subtypes = {
#     'PCM_S8':    0x0001,  # Signed 8 bit data
#     'PCM_16':    0x0002,  # Signed 16 bit data
#     'PCM_24':    0x0003,  # Signed 24 bit data
#     'PCM_32':    0x0004,  # Signed 32 bit data
#     'PCM_U8':    0x0005,  # Unsigned 8 bit data (WAV and RAW only)
#     'FLOAT':     0x0006,  # 32 bit float data
#     'DOUBLE':    0x0007,  # 64 bit float data
#     'ULAW':      0x0010,  # U-Law encoded.
#     'ALAW':      0x0011,  # A-Law encoded.
#     'IMA_ADPCM': 0x0012,  # IMA ADPCM.
#     'MS_ADPCM':  0x0013,  # Microsoft ADPCM.
#     'GSM610':    0x0020,  # GSM 6.10 encoding.
#     'VOX_ADPCM': 0x0021,  # OKI / Dialogix ADPCM
#     'G721_32':   0x0030,  # 32kbs G721 ADPCM encoding.
#     'G723_24':   0x0031,  # 24kbs G723 ADPCM encoding.
#     'G723_40':   0x0032,  # 40kbs G723 ADPCM encoding.
#     'DWVW_12':   0x0040,  # 12 bit Delta Width Variable Word encoding.
#     'DWVW_16':   0x0041,  # 16 bit Delta Width Variable Word encoding.
#     'DWVW_24':   0x0042,  # 24 bit Delta Width Variable Word encoding.
#     'DWVW_N':    0x0043,  # N bit Delta Width Variable Word encoding.
#     'DPCM_8':    0x0050,  # 8 bit differential PCM (XI only)
#     'DPCM_16':   0x0051,  # 16 bit differential PCM (XI only)
#     'VORBIS':    0x0060,  # Xiph Vorbis encoding.
#     'ALAC_16':   0x0070,  # Apple Lossless Audio Codec (16 bit).
#     'ALAC_20':   0x0071,  # Apple Lossless Audio Codec (20 bit).
#     'ALAC_24':   0x0072,  # Apple Lossless Audio Codec (24 bit).
#     'ALAC_32':   0x0073,  # Apple Lossless Audio Codec (32 bit).
# }
#
# _endians = {
#     'FILE':   0x00000000,  # Default file endian-ness.
#     'LITTLE': 0x10000000,  # Force little endian-ness.
#     'BIG':    0x20000000,  # Force big endian-ness.
#     'CPU':    0x30000000,  # Force CPU endian-ness.
# }
#
# # libsndfile doesn't specify default subtypes, these are somehow arbitrary:
# _default_subtypes = {
#     'WAV':   'PCM_16',
#     'AIFF':  'PCM_16',
#     'AU':    'PCM_16',
#     # 'RAW':  # subtype must be explicit!
#     'PAF':   'PCM_16',
#     'SVX':   'PCM_16',
#     'NIST':  'PCM_16',
#     'VOC':   'PCM_16',
#     'IRCAM': 'PCM_16',
#     'W64':   'PCM_16',
#     'MAT4':  'DOUBLE',
#     'MAT5':  'DOUBLE',
#     'PVF':   'PCM_16',
#     'XI':    'DPCM_16',
#     'HTK':   'PCM_16',
#     'SDS':   'PCM_16',
#     'AVR':   'PCM_16',
#     'WAVEX': 'PCM_16',
#     'SD2':   'PCM_16',
#     'FLAC':  'PCM_16',
#     'CAF':   'PCM_16',
#     'WVE':   'ALAW',
#     'OGG':   'VORBIS',
#     'MPC2K': 'PCM_16',
#     'RF64':  'PCM_16',
# }