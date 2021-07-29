#!/usr/bin/python

import serial
import struct
import time
import logging

FORMAT = '%(asctime)-15s %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__name__)

# port='/dev/cu.BittleSPP-3534C8-Port'
# port='/dev/ttyS0'  # needed when using RaspberryPi
# port = '/dev/cu.wchusbserial1430'  # needed when using Mac USB


def encode(in_str, encoding='utf-8'):
    if isinstance(in_str, bytes):
        return in_str
    else:
        return in_str.encode(encoding)


def get_serial(port='/dev/cu.wchusbserial1430'):
    return serial.Serial(
        port=port,
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )


def open_serial(ser):
    if ser.is_open:
        ser.close()
    logger.info('serial port is opening, please wait for 5 secs')
    ser.open()
    time.sleep(5)


def close_serial(ser):
    if ser.is_open:
        ser.close()
    logger.info('closing serial port')
    ser.close()
    time.sleep(2)


def execute(ser, cmd):
    cmd_split = cmd.split(' ')
    # print(cmd, cmd_split)
    if len(cmd_split) == 1:
        task = [cmd, 0]
    else:
        task = [cmd[0], cmd_split, 0]
    wrapper(ser, task)
    return task


def wrapper(ser, task):  # task Structure is [token, var=[], time]
    logger.debug(f'wrapper, task={task}')
    if len(task) == 2:
        serial_write_byte(ser, [task[0]])
    elif isinstance(task[1][0], int):
        serial_write_num2byte(ser, task[0], task[1])
    else:
        serial_write_byte(ser, task[1])
    time.sleep(task[-1])


def serial_write_num2byte(ser, token, var=None):  # Only to be used for c m u b i l o within Python
    # print("Num Token "); print(token);print(" var ");print(var);print("\n\n");
    logger.debug(f'serial_write_num2byte, token={token}, var={var}')
    in_str = ''
    if var is None:
        var = []
    if token == 'l' or token == 'i':
        var = list(map(int, var))
        in_str = token.encode() + struct.pack('b' * len(var), *var) + '~'.encode()
    elif token == 'c' or token == 'm' or token == 'u' or token == 'b':
        in_str = token + str(var[0]) + " " + str(var[1]) + '\n'
    logger.debug(f"serial_write_num2byte: {in_str}\n")
    ser.write(encode(in_str))


def serial_write_byte(ser, var=None):
    logger.debug(f'serial_write_byte, var={var}')
    token = var[0][0]
    if (token == 'c' or token == 'm' or token == 'b' or token == 'u') and len(var) >= 2:
        in_str = ''
        for element in var:
            in_str = in_str + element + " "
    elif token == 'l' or token == 'i':
        if len(var[0]) > 1:
            var.insert(1, var[0][1:])
        var[1:] = list(map(int, var[1:]))
        in_str = token.encode() + struct.pack('b' * (len(var) - 1), *var[1:]) + '~'.encode()
    elif token == 'w' or token == 'k':
        in_str = var[0] + '\n'
    else:
        in_str = token
    logger.debug(f"serial_write_byte: {in_str}\n")
    ser.write(encode(in_str))


if __name__ == '__main__':
    port = '/dev/cu.wchusbserial1430'  # needed when using Mac
    ser = get_serial()
    while True:
        try:
            cmd = input('input command please >>\n')
            cmd_split = cmd.split(' ')
            print(cmd, cmd_split)
            if len(cmd_split) == 1:
                wrapper(ser, [cmd, 0])
            else:
                wrapper(ser, [cmd[0], cmd_split, 0])

        except KeyboardInterrupt:
            break
    if ser.is_open:
        ser.close()
        print('\nclose')


# if __name__ == '__main__':
#     counter = 0
#     time.sleep(2)
#     print(len(sys.argv))
#     if len(sys.argv) >= 2:
#         if len(sys.argv) == 2:
#             wrapper([sys.argv[1], 0])
#         else:
#             #    print [sys.argv[1][0],sys.argv[1:],0]
#             wrapper([sys.argv[1][0], sys.argv[1:], 0])
#     else:
#         while True:
#             for a in np.arange(0, 2 * math.pi, 0.2):
#                 print(a)
#                 serial_write_byte(["ksit"])
#                 time.sleep(0.04)
#
#     while True:
#         time.sleep(0.01)
#         counter = counter + 1
#         if counter > 1000:
#             break
#         # print("number of chars:" +str(ser.in_waiting))
#         if ser.in_waiting > 0:
#             x = ser.readline()
#             if x != "":
#                 print(x),
