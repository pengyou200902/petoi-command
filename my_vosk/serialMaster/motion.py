import ardSerial
from serial import Serial
from typing import Text, List


import logging

LOG_FORMAT = '%(asctime)-15s %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

number_of_joints = 16


def log_msg(logger: logging.Logger, msg, kind):
    if msg:
        if kind == 'i':
            logger.info(msg)
        if kind == 'w':
            logger.warning(msg)
        if kind == 'e':
            logger.error(msg)
        if kind == 'd':
            logger.debug(msg)


class Joint:
    def __init__(self, index=-1, angle=0, name=''):
        self.index = index
        self.angle = angle
        self.name = name

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, val: int = 0):
        if 1 <= val <= 7 or val < 0 or val > 15:
            msg = f'index should be in [0 or 8~15], but now index={val}'
            logger.error(msg)
            raise ValueError(msg)
        else:
            self._index = val

    @property
    def angle(self) -> int:
        return self._angle

    @angle.setter
    def angle(self, val: int = 0):
        if val < -9 or val > 9:
            msg = f'val should be in [-9, 9], but now angle={val}'
            logger.error(msg)
            raise ValueError(msg)
        self._angle = val

    @property
    def name(self) -> Text:
        return self._name

    @name.setter
    def name(self, val: Text):
        if val:
            self._name = val
        else:
            msg = "A joint should have a name."
            logger.error(msg)
            raise ValueError(msg)


class MotionFrame:
    def __init__(self, frame: List[List[int]]):
        self.frame = frame

    @property
    def frame(self) -> List:
        return self._frame

    @frame.setter
    def frame(self, val: List[List[int]]):
        if len(val) >= 20:
            self._frame = val
        else:
            msg = "A MotionFrame should have a valid frame that indicates joints' status/angles."
            logger.error(msg)
            raise ValueError(msg)


class Skill:
    def __init__(self,
                 name: Text,
                 command: Text,
                 frames: List[List[MotionFrame]],
                 description: Text,
                 angle_ratio: int = 1):
        self.name = name
        self.command = command
        self.frames = frames
        self.description = description
        self.angle_ratio = angle_ratio

    @property
    def name(self) -> Text:
        return self._name

    @name.setter
    def name(self, val: Text):
        if val:
            self._name = val
        else:
            msg = "A Skill should have a name."
            logger.error(msg)
            raise ValueError(msg)

    @property
    def command(self) -> Text:
        return self._command

    @command.setter
    def command(self, val: Text):
        if val:
            self._command = val
        else:
            msg = "A Skill should have a corresponding command."
            logger.error(msg)
            raise ValueError(msg)

    @property
    def frames(self) -> List:
        return self._frames

    @frames.setter
    def frames(self, val: List):
        if len(val) <= 0:
            msg = "A Skill should have corresponding frames of joints."
            logger.error(msg)
            raise ValueError(msg)
        else:
            self._frames = val

    @property
    def description(self) -> Text:
        return self._description

    @description.setter
    def description(self, val: Text):
        if val:
            self._description = val
        msg = "A Skill should have a description."
        logger.error(msg)
        raise ValueError(msg)

    @property
    def angle_ratio(self) -> int:
        return self._angle_ratio

    @angle_ratio.setter
    def angle_ratio(self, val: int):
        if val == 1 or val == 2:
            self._angle_ratio = val
        else:
            msg = "An angle ration should be 1 or 2."
            logger.error(msg)
            raise ValueError(msg)

    def perform(self, ser: Serial) -> List:
        cmd_split = self.command.split(' ')
        # print(cmd, cmd_split)
        if len(cmd_split) == 1:
            task = [self.command, 0]
        else:
            task = [self.command[0], cmd_split, 0]
        ardSerial.wrapper(ser, task)
        return task


names = {}
names[0] = 'neck'
names[8] = 'left front shoulder'
names[9] = 'right front shoulder'
names[10] = 'right back shoulder'
names[11] = 'left back shoulder'
names[12] = 'left front knee'
names[13] = 'right front knee'
names[14] = 'right back knee'
names[15] = 'left back knee'
joints = {}
for i in range(number_of_joints):
    if not 1 <= i <= 7:
        joints[i] = Joint(index=i, name=names[i])

# -------------------------For test-------------------------------
# zero_status = [1, 0, 0, 1,
#                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# zero_motion = MotionFrame(zero_status)
# crF = [
#     [55,  57,  51,  56, -15, -19,  -7, -16],
#     [59,  51,  54,  49, -15, -19,  -7, -16],
#     [62,  45,  57,  44, -14, -18,  -6, -15],
#     [65,  38,  60,  38, -13, -15,  -5, -13],
#     [68,  31,  63,  31, -11, -12,  -4, -10],
#     [71,  24,  65,  25, -10,  -9,  -2,  -7],
#     [73,  19,  68,  20,  -8,  -5,   0,  -4],
#     [75,  16,  69,  16,  -5,  -2,   3,   2],
#     [77,  14,  71,  13,  -2,   1,   6,   8],
#     [78,  15,  71,  14,   2,   1,  10,   8],
#     [79,  20,  75,  19,   0,  -3,   4,   5],
#     [80,  25,  77,  24,  -3,  -5,  -1,   2],
#     [81,  30,  77,  28,  -5,  -8,  -5,  -1],
#     [78,  34,  75,  32, -10, -10,  -8,  -3],
#     [76,  39,  72,  36, -13, -12, -11,  -4],
#     [72,  43,  68,  41, -16, -13, -14,  -6],
#     [67,  48,  64,  45, -18, -14, -15,  -6],
#     [61,  52,  59,  49, -19, -15, -16,  -7],
#     [56,  57,  54,  52, -19, -15, -16,  -7],
#     [50,  61,  48,  56, -19, -15, -16,  -6],
#     [42,  64,  43,  59, -17, -13, -14,  -6],
#     [35,  67,  36,  62, -15, -12, -12,  -4],
#     [29,  70,  30,  64, -12, -11,  -9,  -3],
#     [22,  72,  24,  67,  -8,  -9,  -6,  -1],
#     [17,  74,  19,  68,  -4,  -6,  -3,   1],
#     [16,  76,  15,  70,  -2,  -3,   2,   5],
#     [14,  77,  12,  71,   1,   0,   9,   8],
#     [16,  78,  15,  73,   0,   2,   7,   8],
#     [21,  80,  20,  76,  -3,  -2,   3,   1],
#     [26,  81,  25,  78,  -6,  -4,   1,  -3],
#     [31,  79,  29,  76,  -9,  -8,  -2,  -6],
#     [35,  77,  34,  73, -11, -12,  -3, -10],
#     [40,  74,  38,  70, -12, -15,  -5, -12],
#     [44,  69,  42,  67, -13, -17,  -6, -15],
#     [49,  64,  46,  61, -14, -18,  -6, -16],
#     [53,  58,  50,  57, -15, -19,  -7, -16],
# ]


# import time
# def execute(ser, cmd):
#     cmd_split = cmd.split(' ')
#     # print(cmd, cmd_split)
#     if len(cmd_split) == 1:
#         task = [cmd, 0]
#     else:
#         task = [cmd[0], cmd_split, 0]
#     ardSerial.wrapper(ser, task)
#     return task
#
# ser = ardSerial.get_serial()
# ardSerial.open_serial(ser)
# # execute(ser, 'd')
# input("开始")
# for status in crF:
#     for i, x in enumerate(status):
#         cmd = f'm{i+8} {x}'
#         execute(ser, cmd)
#         time.sleep(0.1)
# print("end motion")
# ardSerial.close_serial(ser)
# -------------------------For test-------------------------------

# [
# 36, 0, -3, 1,
#   55,  57,  51,  56, -15, -19,  -7, -16,
#   59,  51,  54,  49, -15, -19,  -7, -16,
#   62,  45,  57,  44, -14, -18,  -6, -15,
#   65,  38,  60,  38, -13, -15,  -5, -13,
#   68,  31,  63,  31, -11, -12,  -4, -10,
#   71,  24,  65,  25, -10,  -9,  -2,  -7,
#   73,  19,  68,  20,  -8,  -5,   0,  -4,
#   75,  16,  69,  16,  -5,  -2,   3,   2,
#   77,  14,  71,  13,  -2,   1,   6,   8,
#   78,  15,  71,  14,   2,   1,  10,   8,
#   79,  20,  75,  19,   0,  -3,   4,   5,
#   80,  25,  77,  24,  -3,  -5,  -1,   2,
#   81,  30,  77,  28,  -5,  -8,  -5,  -1,
#   78,  34,  75,  32, -10, -10,  -8,  -3,
#   76,  39,  72,  36, -13, -12, -11,  -4,
#   72,  43,  68,  41, -16, -13, -14,  -6,
#   67,  48,  64,  45, -18, -14, -15,  -6,
#   61,  52,  59,  49, -19, -15, -16,  -7,
#   56,  57,  54,  52, -19, -15, -16,  -7,
#   50,  61,  48,  56, -19, -15, -16,  -6,
#   42,  64,  43,  59, -17, -13, -14,  -6,
#   35,  67,  36,  62, -15, -12, -12,  -4,
#   29,  70,  30,  64, -12, -11,  -9,  -3,
#   22,  72,  24,  67,  -8,  -9,  -6,  -1,
#   17,  74,  19,  68,  -4,  -6,  -3,   1,
#   16,  76,  15,  70,  -2,  -3,   2,   5,
#   14,  77,  12,  71,   1,   0,   9,   8,
#   16,  78,  15,  73,   0,   2,   7,   8,
#   21,  80,  20,  76,  -3,  -2,   3,   1,
#   26,  81,  25,  78,  -6,  -4,   1,  -3,
#   31,  79,  29,  76,  -9,  -8,  -2,  -6,
#   35,  77,  34,  73, -11, -12,  -3, -10,
#   40,  74,  38,  70, -12, -15,  -5, -12,
#   44,  69,  42,  67, -13, -17,  -6, -15,
#   49,  64,  46,  61, -14, -18,  -6, -16,
#   53,  58,  50,  57, -15, -19,  -7, -16,
# ]