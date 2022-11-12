import sys
from os.path import exists
import logging
import struct

from sonypy_val import *
from sonypy import *

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
    raw_header = f.read(16)
    logging.info(raw_header)
    header = Header(raw_header)
    logging.info(header.tobytes())
    logging.info(header.magic)
    logging.info(header.CTE)
    logging.info(header.op_cnt)
    return header


def get_object_pointer(f):
    raw_object_pointer = f.read(16)
    logging.info(raw_object_pointer)
    obj_pt = ObjectPointer(raw_object_pointer)
    logging.info(obj_pt.tobytes())
    logging.info(obj_pt.magic)
    logging.info(obj_pt.offset)
    logging.info(obj_pt.length)
    return obj_pt


def get_object(f):
    raw_obj = f.read(16)
    logging.info(raw_obj)
    obj = Object(raw_obj)
    logging.info(obj.tobytes())
    logging.info(obj.magic)
    logging.info(obj.track_cnt)
    logging.info(obj.track_sz)
    return obj


def get_track(f):
    raw_track = f.read(16)
    track = Track(raw_track)

    # Fill track info with tags
    for i in range(0, track.tag_len):
        logging.info('%d-th tag:', i)

        # Fill this track with this tag
        raw_tag = f.read(track.tag_sz)
        filled, tag_type, tag_val = track.fill_in_tags(raw_tag)
        if not filled:
             logging.warning('track %d-tag tag_type unknown %s', i, tag_type)

    logging.info(str(track))
    return track

def read_all_tracks(device_path):
    tracks = []
    with open(device_path+'/'+AUDIO_P+'/'+CNTINF_F, 'rb') as f:
        logging.info('read header')
        header = get_header(f)
        logging.info('read object header')
        obj_p = get_object_pointer(f)
        logging.info('object')
        obj = get_object(f)
        logging.info('track')
        for i in range(0, obj.track_cnt):
            track = get_track(f)
            tracks.append(track)
    return tracks


def print_help():
    print('Usage:')
    print('python3 sonypy.py [device] [option] [dir/soungname]')


if __name__ == "__main__":
    logging.basicConfig(filename='sonypy.log', level=logging.WARNING)
    if len(sys.argv) < 2:
        print_help()
        exit(1)

    # check the device is valid device or not
    ret = valid_device(sys.argv[1])
    if (ret == 'wrongdev') or (ret == 'nodev') or (ret == 'empty'):
        print(ret)
        exit(1)

    print('Found walkman')
    tracks = read_all_tracks(sys.argv[1])
    for track in tracks:
        print(track)
