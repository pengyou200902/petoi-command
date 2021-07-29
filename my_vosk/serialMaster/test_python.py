import struct


var = ['i', 1, 0, 0, 1, 0, 2, 0]
print([*var])
print(struct.pack('b' * (len(var)-1), *var[1:]))
print('1001020')


