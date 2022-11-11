import sys
from os.path import exists
import struct

from sonypy_val import *

def valid_device(device_path):
    if not device_path:
        return 'empty'

    if exists(device_path):
        # check the omgaudio/cntinfo.dat
        if exists(device_path+'/'+AUDIO_P+'/'+CNTINF_F):
            return 'valid'
        else: 
            return 'wrongdev'
    else:
        return 'nodev'


# get header from cntinf.dat
def get_header(f):
    f.seek(0)
    header = f.read()[0:16]
    magic = (header[0:4]).decode('utf-8')
    cte = struct.unpack('<I', header[4:8])[0] # constant number
    obj_cnt = header[8]
    print(magic)
    print(cte)
    print(obj_cnt)


def get_object_pointer(f):
    f.seek(0)
    object_pointer = f.read()[16:32]
    magic = (object_pointer[0:4]).decode('utf-8')
    offset = struct.unpack('>I', object_pointer[4:8])[0]
    length = struct.unpack('>I', object_pointer[8:12])[0]
    print(magic)
    print(offset)
    print(length)


def get_object(f):
    f.seek(0)
    obj = f.read()[32:44]
    magic = (obj[0:4]).decode('utf-8')
    count = struct.unpack('>H', obj[4:6])[0]
    size = struct.unpack('>H', obj[6:8])[0]
    print(magic)
    print(count)
    print(size)


def read_all_tracks(device_path):
    #with open(deivce_path+'/'+AUDIO_P+'/'+CNTINF_F, 'rb') as cntinf_f:
    with open(device_path+'/'+AUDIO_P+'/'+CNTINF_F, 'rb') as f:
        print('read header')
        get_header(f)
        print('read object header')
        get_object_pointer(f)
        print('object')
        get_object(f)


def print_help():
    print('Usage:')
    print('python3 sonypy.py [device] [option] [dir/soungname]')


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print_help()
        exit(1)

    # check the device is valid device or not
    ret = valid_device(sys.argv[1])
    if (ret == 'wrongdev') or (ret == 'nodev') or (ret == 'empty'):
        print(ret)
        exit(1)

    print('Found walkman')
    read_all_tracks(sys.argv[1])
