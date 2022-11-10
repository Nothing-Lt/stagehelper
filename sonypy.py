import sys
from os.path import exists

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
def get_header(file_name):
    f = open(file_name, 'rb')
    header = f.read()[0:16]
    magic = (header[0:4]).decode('utf-8')
    cte = header[4:8] # constant number
    obj_cnt = 0
    padding = 0
    print(magic)
    print(cte)
    f.close()


def read_all_tracks(device_path):
    #with open(deivce_path+'/'+AUDIO_P+'/'+CNTINF_F, 'rb') as cntinf_f:
    get_header(device_path+'/'+AUDIO_P+'/'+CNTINF_F)

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
