import struct
import re

def is_number(number):
    return bool(re.match(r'^-?\d+(\.\d+)?$', number))

# float to bytes
def float_to_bytes(f):
    return struct.pack('f', f)

# bytes to float
def bytes_to_float(b):
    return struct.unpack('f', b)[0]

def double_to_bytes(d):
    return struct.pack('d', d)

def bytes_to_double(b):
    return struct.unpack('d', b)[0]

def str_to_list(s: str) -> list:
    """将字符串转换为字符列表."""
    return list(s)


def list_to_str(lst: list) -> str:
    """将字符列表连接成一个字符串."""
    return ''.join(lst)

def list_to_hex(data):
    out = 0
    for i in range(len(data)):
        if data[i] == 'X':
            data[i] = '0'
        out |= int(data[i])<<i
    return hex(out)

def list_to_hex_2(data):
    out = 0
    for i in range(len(data)-1,-1,-1):
        if data[i] == 'X':
            data[i] = '0'
        out |= int(data[i]) << (len(data) - i - 1)
    return hex(out)

if __name__ == '__main__':
    # test = bytes([0xaf,0x7b,0x52,0xcb])
    test = bytes([0x1b, 0x10, 0x82, 0x43])
    test = bytes([0xbf, 0xc9, 0xf2, 0x44])
    print(bytes_to_float(test))
    # a = double_to_bytes(3.14)
    # print(len(a),a)
    # print(bytes_to_double(a))
    # s = "COM3"
    # char_list = str_to_list(s)
    # print(char_list)
    # joined_str = list_to_str(char_list)
    # print(joined_str)
