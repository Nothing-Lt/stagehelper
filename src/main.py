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
    print('Found walkman %s' % dev_path)
    print('Disk Size: %dMB, Used: %dMB(%02f), Free: %dMB(%02f)' % 
        (player.total/(2**20), 
        player.used/(2**20), player.used/player.total, 
        player.free/(2**20), player.free/player.total))
    print('Adding songs:')
    print('===================================================')

    obj = Object()
    if 'audio_dir' in locals():
        need_size = 0
        entries = scandir(audio_dir)
        for entry in entries:
            if entry.name.endswith('.mp3'):
                print('=> %s '% entry.name)
                obj.add_track(Track(entry.path))
                need_size += entry.stat(follow_symlinks=False).st_size
        print('With the file in %s need %dMB' % (audio_dir, ceil(need_size/(2**20))))
    else:
        if audio_f.endswith('.mp3'):
            obj.add_track(Track(audio_f))
        need_size = getsize(audio_f)
        print('With the file %s need %dMB' % (audio_f, ceil(need_size/(2**20))))

    artist_lst = db.get_artist_list(obj.tracks)
    album_lst = db.get_album_list(obj.tracks)
    genre_lst = db.get_genre_list(obj.tracks)
    print('===================================================')

    # write to database
    print('Writing 00GTRLST')
    db.write_00GTRLST()
    print('Writing 01TREEXX author')
    db.write_01TREEXX(artist_lst, obj.tracks, 'author', 2)
    print('Writing 01TREEXX album')
    db.write_01TREEXX(album_lst, obj.tracks, 'album', 1)
    print('Writing 01TREEXX album')
    db.write_01TREEXX(album_lst, obj.tracks, 'album', 3)
    print('Writing 01TREEXX genre')
    db.write_01TREEXX(genre_lst, obj.tracks, 'genre', 4)
    print('Writing 01TREE22')
    db.write_01TREE22()
    print('Writing 02TREINF')
    db.write_02TREINF(obj.tracks)
    print('Writing 03GINF03')
    db.write_03GINF03(obj.tracks)
    print('Writing 03GINF22')
    db.write_03GINF22()
    print('Writing 04CNTINF')
    db.write_04CNTINF(obj.tracks)
    print('Writing 05CIDLST')
    db.write_05CIDLST(obj.tracks)

    # sync music to player
    print('Syncing tracks')
    db.sync_tracks(obj.tracks)
