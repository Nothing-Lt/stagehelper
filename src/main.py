import sys
from os.path import isdir, getsize
from os import path, mkdir, scandir, listdir
from math import ceil
import logging
import struct

import psutil

from Database import *
from sonypy_var import *
from Header import *
from ObjectPointer import *
from Object import *
from Track import *

def valid_device(device_path):
    if not device_path:
        return 'empty'

    if path.exists(device_path):
        # check the omgaudio/cntinfo.dat
        if path.exists(device_path+'/'+AUDIO_P+'/'+CNTINF_F):
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

        # bind this track with actual file
        track.bind_with_file('dummy.dat')

    logging.info(str(track))
    return track

def read_all_tracks(device_path):
    tracks = []
    with open(device_path+'/'+AUDIO_P+'/'+CNTINF_F, 'rb') as f:
        logging.info('read header')
        header = get_header(f)
        logging.info('read object header')
        obj_pt = get_object_pointer(f)
        logging.info('object')
        obj = get_object(f)
        logging.info('track')
        for i in range(0, obj.track_cnt):
            track = get_track(f)
            tracks.append(track)
    return header, obj_pt, obj, tracks


def print_help():
    print('Usage:')
    print('python3 main.py [device] [option] [dir/soungname]')


if __name__ == "__main__":
    logging.basicConfig(filename='sonypy.log', level=logging.WARNING)

    if len(sys.argv) < 2:
        print_help()
        exit(1)

    dev_path = sys.argv[1]
    if isdir(sys.argv[2]):
        audio_dir = sys.argv[2]
    else:
        audio_f = sys.argv[2]

    db = Database()
    # check the device is valid device or not
    ret = db.set_device(dev_path)
    if (ret == 'wrongdev') :
        create_file = input('Restore the Walkman filesystem?[Y/n]')
        if create_file == 'Y' or create_file == 'y':
            db.restore_filesystem()
    elif (ret == 'nodev') or (ret == 'empty'):
        print(ret)
        exit(2)

    player = psutil.disk_usage(dev_path)
    print('Found walkman')
    print('Disk Size: %dMB, Used: %dMB(%02f), Free: %dMB(%02f)' % 
        (player.total/(2**20), 
        player.used/(2**20), player.used/player.total, 
        player.free/(2**20), player.free/player.total))

    obj = Object()
    if 'audio_dir' in locals():
        need_size = 0
        entries = scandir(audio_dir)
        for entry in entries:
            if entry.name.endswith('.mp3'):
                print(entry.name)
                obj.add_track(Track(entry.path))
                need_size += entry.stat(follow_symlinks=False).st_size
        print('With the file in %s need %dMB' % (audio_dir, ceil(need_size/(2**20))))
    else:
        need_size = getsize(audio_f)
        print('With the file %s need %dMB' % (audio_f, ceil(need_size/(2**20))))

    artist_lst = db.get_artist_list(obj.tracks)
    db.write_01TREEXX(artist_lst, obj.tracks, 'author', 2)
    album_lst = db.get_album_list(obj.tracks)
    db.write_01TREEXX(album_lst, obj.tracks, 'album', 1)
    db.write_01TREEXX(album_lst, obj.tracks, 'album', 3)
    genre_lst = db.get_genre_list(obj.tracks)
    db.write_01TREEXX(genre_lst, obj.tracks, 'genre', 4)
    db.write_00GTRLST()
    db.write_03GINF22()
    db.write_04CNTINF(obj.tracks)
    db.write_02TREINF(obj.tracks)
    exit(0)

    track = Track(audio_f)

    header = Header()
    obj_pt = ObjectPointer() 
    obj = Object()
    obj.add_track(track)

    idx = 1
    tracks = obj.tracks
    for track in tracks:

        dir_name = '%s%s/10F%02x' % (dev_path, AUDIO_P, (idx >> 8))
        track.oma_name = '1%07x.OMA' % idx

        if not isdir(dir_name):
            mkdir(dir_name)
        track.generate_oma(dir_name)

        idx = idx + 1

    f = open(dev_path + AUDIO_P + '/' + CNTINF_F, 'wb+')
    track_bytestream = bytearray()
    for track in tracks:
        track_bytestream = track_bytestream + track.tobytes()
    f.write(header.tobytes())
    f.write(obj_pt.tobytes())
    f.write(obj.tobytes())
    f.write(track_bytestream)
    f.close()

