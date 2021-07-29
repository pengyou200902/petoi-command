#!/usr/bin/python
from ardSerial import *

import serial
import struct
import sys
import time
import math
import numpy as np

port = '/dev/cu.wchusbserial1430'  # needed when using Mac
ser = get_serial(port)
time.sleep(6)

schedule = [['m', [1, 45], 1],
            ['d', 3],
            ['m', [1, -30], 1],
            ['d', 2],
            ['b', '10', '255', 1],
            ['ktr', 3],
            ['d', 2]]

try:
    for task in schedule:
        wrapper(ser, task)

    for i in range(1000):
        # serial_write_byte(ser, ["i",
        #                         "0",
        #                         str(int(15 * math.sin(2 * math.pi * i / 100))),
        #                         "1",
        #                         str(int(15 * math.sin(4 * math.pi * i / 100))),
        #                         "2",
        #                         str(int(15 * math.sin(2 * math.pi * i / 100)))])
        #
        # serial_write_num2byte(ser, "i", [0,
        #                                  int(15 * math.sin(2 * math.pi * i / 100)),
        #                                  1,
        #                                  int(15 * math.sin(4 * math.pi * i / 100)),
        #                                  2,
        #                                  int(15 * math.sin(2 * math.pi * i / 100))])
        #
        # serial_write_byte(ser, ["m", "1", "10"])
        #
        # ser.write("m1 10\n".encode())
        #
        # wrapper(ser, ['i', [0,
        #                     30 * math.sin(4 * math.pi * i / 500),
        #                     1,
        #                     30 * math.sin(4 * math.pi * i / 500 + math.pi / 2),
        #                     2,
        #                     30 * math.cos(4 * math.pi * i / 500)],
        #               1])

        # serialWriteNumToByte(['c'])

        if i % 250 == 0:
            print("should stop")
            time.sleep(1)
            print("should start")
        time.sleep(0.012)

    ser.close()

except Exception as e:
    ser.close()
    raise e
