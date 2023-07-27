
import struct

from os.path import isdir
from os import mkdir
from tqdm import tqdm

from sonypy_var import *
from Header import *
from ObjectPointer import *
from Object import *
from Track import *
from Tag import *
from sonypy_var import *

class Database():
    def __init__(self):
        self.device_path = ''
        self.audio_path = ''
        return

    def set_device(self, device_path):
        if not device_path:
            return 'empty'

        if path.exists(device_path):
            # check the omgaudio/cntinfo.dat
            self.device_path = device_path
            self.audio_path = device_path + '/' + AUDIO_P
            if path.exists(device_path+'/'+AUDIO_P+'/'+CNTINF_F):
                return 'valid'
            else: 
                return 'wrongdev'
        else:
            return 'nodev'

    def restore_filesystem(self):
        if not path.exists(self.audio_path):
            mkdir(self.audio_path)

        f = open(self.audio_path + '/' + CNTINF_F, 'wb+')
        header = Header()
        obj_pt = ObjectPointer()
        obj = Object()
        f.write(header.tobytes() + obj_pt.tobytes() + obj.tobytes())
        f.close()

    def write_00GTRLST(self):
        header = Header()
        header.magic = 'GTLT'
        header.CTE = bytearray([1,1,0,0])
        header.op_cnt = 2

        obj_pt1 = ObjectPointer()
        obj_pt1.magic = 'SYSB'
        obj_pt1.offset = 0x30
        obj_pt1.length = 0x70

        obj_pt2 = ObjectPointer()
        obj_pt2.magic = 'GTLB'
        obj_pt2.offset = 0xA0
        obj_pt2.length = 0xAB0

        obj1 = Object()
        obj1.magic = 'SYSB'
        obj1.track_cnt = 1
        obj1.track_sz = 80
        obj1.padding = struct.pack('<2I', 0xD0, 0)
        obj1_blk = bytearray([0] * 96)

        obj2 = Object()
        obj2.magic = 'GTLB'
        obj2.track_cnt = 34
        obj2.track_sz = 80
        obj2.padding = struct.pack('>I', 5) + struct.pack('<I',3)

        first_blk = bytearray([0,1,0,1] + [0] *12)
        first_blk = first_blk + bytearray([0,1] + [0] * 14)
        first_blk = first_blk + bytearray([0] * 48)

        second_blk = bytearray([0,2,0,3] + [0] * 12)
        second_blk = second_blk + bytearray([0,1,0,0]) + bytes('TPE1','utf-8')[0:4] + bytearray([0] * 8)
        second_blk = second_blk + bytearray([0] * 48)

        third_blk = bytearray([0,3,0,3] + [0] * 12)
        third_blk = third_blk + bytearray([0,1,0,0]) + bytes('TALB','utf-8')[0:4] + bytearray([0] * 8)
        third_blk = third_blk + bytearray([0] * 48)

        fourth_blk = bytearray([0,4,0,3] + [0] * 12)
        fourth_blk = fourth_blk + bytearray([0,1,0,0]) + bytes('TCON','utf-8')[0:4] + bytearray([0] * 8)
        fourth_blk = fourth_blk + bytearray([0] * 48)

        fifth_blk = bytearray([0,0x22,0,2] + [0] * 12)
        fifth_blk = fifth_blk + bytearray([0] * 64)

        blk_data = first_blk + second_blk + third_blk + fourth_blk + fifth_blk

        for j in range(5,34):
            blk = bytearray([0,j] + [0] * 78)
            blk_data = blk_data + blk

        filepath = '%s/%s' % (self.audio_path, '00GTRLST.DAT') 
        f = open(filepath, 'wb+')
        if f is None:
            print('Cannot get file %s' % filepath)
            return
        f.write(header.tobytes() + obj_pt1.tobytes() + obj_pt2.tobytes() + obj1.tobytes() + obj1_blk + obj2.tobytes() + blk_data)
        f.close()


    def write_01TREEXX(self, cat, tracks, attr, type_id):
        track_cnt = len(tracks)
        cat_cnt = len(cat)

        header = Header()
        header.magic = 'TREE'
        header.CTE = bytearray([1,1,0,0])
        header.op_cnt = 2

        obj_pt1 = ObjectPointer()
        obj_pt1.magic = 'GPLB'
        obj_pt1.offset = 0x30
        obj_pt1.length = 16400

        obj_pt2 = ObjectPointer()
        obj_pt2.magic = 'TPLB'
        obj_pt2.offset = 0x4040
        obj_pt2.length = (16+ (track_cnt * 2) + (16 - (track_cnt * 2) % 16))

        obj = Object()
        obj.magic = 'GPLB'
        obj.track_cnt = cat_cnt
        obj.track_sz = 8
        obj.padding = struct.pack('>2I', obj.track_cnt, 0)

        index = 1
        indexTPLB = 1

        data_blk = bytearray()
        for e in cat:
            blk = struct.pack('>H', index)
            blk += struct.pack('>H', 0x100)
            blk += struct.pack('>H', indexTPLB)
            blk += struct.pack('<H', 0)
            data_blk += blk

            # if (type_id == 1) or (type_id == 3):
            for track in tracks[indexTPLB-1:]:
                if str(track.tags[attr].val) != e:
                    break

            indexTPLB = tracks.index(track)
            index += 1

        index -= 1
        padding = bytearray([0] * (16384 - (index * 8)))

        obj2 = Object()
        obj2.magic = 'TPLB'
        obj2.track_cnt = track_cnt
        obj2.track_sz = 2
        obj2.padding = struct.pack('>2I', obj2.track_cnt, 0)

        index = 0
        idx_blk = bytearray()
        for idx, track in enumerate(tracks):
            blk = struct.pack('>H', idx+1)
            idx_blk += blk
            index += 1

        while (index % 8) != 0:
            blk = struct.pack('>H', 0)
            idx_blk += blk
            index += 1

        all_blk = header.tobytes() + \
                    obj_pt1.tobytes() + obj_pt2.tobytes() + \
                    obj.tobytes() + data_blk + padding + \
                    obj2.tobytes() + idx_blk
        
        filepath = '%s/01TREE%02d.DAT' % (self.audio_path, type_id)
        f = open(filepath, 'wb+')
        if f is None:
            print('Failed open %s' % filepath)
            return
        f.write(all_blk)
        f.close()


    # simple implementation of 03GINF
    def write_03GINF03(self, tracks):
        header = Header()
        header. magic = 'GPIF'
        header.op_cnt = 1

        obj_pt1 = ObjectPointer()
        obj_pt1.magic = 'GPFB'
        obj_pt1.offset = 0x20
        obj_pt1.length = 0xa0 #(TAGSIZE * len(tracks)) + 0x10

        obj1 = Object()
        obj1.magic = 'GPFB'
        obj1.track_cnt = 1 #len(tracks)
        obj1.track_sz = 0x90
        obj1.padding = struct.pack('>2I', 0, 0)

        data_blk = bytearray()
        blk = struct.pack('>H', 0)
        blk += struct.pack('>H', 0)
        blk += struct.pack('>H', 0)
        blk += struct.pack('<H', 0)
        data_blk += blk
        blk = struct.pack('>H', 0)
        blk += struct.pack('>H', 0)
        blk += struct.pack('>H', 0x1)
        blk += struct.pack('<H', 0x8000)
        data_blk += blk

        tag = Tag()
        tag.type = bytes('TIT2','utf-8')[0:4]
        tag.val = 'Unknown'

        all_blk = header.tobytes() + \
                obj_pt1.tobytes() + obj1.tobytes() + \
                data_blk + tag.tobytes(TAGSIZE)
        
        filepath = '%s/03GINF03.DAT' % (self.audio_path)
        f = open(filepath, 'wb+')
        if f is None:
            print('Failed open %s' % filepath)
            return
        f.write(all_blk)
        f.close()


    def write_01TREE22(self):
        header = Header()
        header. magic = 'TREE'
        header.op_cnt = 2

        obj_pt1 = ObjectPointer()
        obj_pt1.magic = 'GPLB'
        obj_pt1.offset = 0x30
        obj_pt1.length = 16

        obj_pt2 = ObjectPointer()
        obj_pt2.magic = 'TPLB'
        obj_pt2.offset = 0x40
        obj_pt2.length = 16

        obj1 = Object()
        obj1.magic = 'GPLB'
        obj1.track_cnt = 0
        obj1.track_sz = 8
        obj1.padding = struct.pack('>2I', 0, 0)

        obj2 = Object()
        obj2.magic = 'TPLB'
        obj2.track_cnt = 0
        obj2.track_sz = 2
        obj2.padding = struct.pack('>2I', 0, 0)

        all_blk = header.tobytes() + obj_pt1.tobytes() + obj_pt2.tobytes() + \
                    obj1.tobytes() + obj2.tobytes()

        filepath = '%s/01TREE22.DAT' % (self.audio_path)
        f = open(filepath, 'wb+')
        if f is None:
            print('Failed open %s' % filepath)
            return
        f.write(all_blk)
        f.close()


    def write_02TREINF(self, tracks):
        header = Header()
        header.magic = 'GTIF'

        obj_pt = ObjectPointer()
        obj_pt.magic = 'GTFB'
        obj_pt.offset = 0x20
        obj_pt.length = 0x2410

        obj = Object()
        obj.magic = 'GTFB'
        obj.track_cnt = 34
        obj.track_sz = 0x90
        obj.padding = struct.pack('>2I', 0, 0)

        track = Track()
        track.ftype = bytearray([0,0,0,0])
        track.time_len = 0
        track.encoding = 0
        track.tag_len = 1
        track.tag_sz = TAGSIZE

        tag = Tag()
        tag.type = bytes('TIT2','utf-8')[0:4]
        track.tags['ph'] = tag

        track_blk = bytearray()
        for i in range(0, 4):
            track_blk += track.tobytes() + tag.tobytes(TAGSIZE)

        padding = bytearray()
        for i in range(0, 540):
            padding += bytearray([0] * 16)

        all_blk = header.tobytes() + obj_pt.tobytes() + obj.tobytes() + track_blk + padding

        filepath = '%s/02TREINF.DAT' % (self.audio_path)
        f = open(filepath, 'wb+')
        if f is None:
            print('Failed open %s' % filepath)
            return
        f.write(all_blk)
        f.close()


    def write_03GINF22(self):
        header = Header()
        header.magic = 'GPIF'
        header.CTE = bytearray([1,1,0,0])
        header.op_cnt = 1

        obj_pt = ObjectPointer()
        obj_pt.magic = 'GPFB'
        obj_pt.offset = 0x20
        obj_pt.length = 16

        obj = Object()
        obj.magic = 'GPFB'
        obj.track_cnt = 0
        obj.track_sz = 784
        obj.padding = struct.pack('<2I', 0, 0)

        filepath = '%s/%s' % (self.audio_path, '03GINF22.DAT')
        f = open(filepath, 'wb+')
        if f is None:
            print('Cannot get file %s' % filepath)
            return
        f.write(header.tobytes() + obj_pt.tobytes() + obj.tobytes())
        f.close()


    def write_04CNTINF(self, tracks):
        header = Header()
        
        obj_pt = ObjectPointer()
        obj_pt.length =  (((TAGSIZE * 5) + 16) * len(tracks)) + 16
        
        obj = Object()
        obj.track_cnt = len(tracks)
        obj.track_sz = (TAGSIZE * 5) + 16
        obj.padding = struct.pack('>2I', 0, 0)

        filepath = '%s/%s' % (self.audio_path, CNTINF_F)
        f = open(filepath, 'wb+')
        track_bytestream = bytearray()
        for track in tracks:
            track_bytestream = track_bytestream + track.tobytes() + track.tags_to_bytes()
        f.write(header.tobytes())
        f.write(obj_pt.tobytes())
        f.write(obj.tobytes())
        f.write(track_bytestream)
        f.close()


    def write_05CIDLST(self, tracks):
        header = Header()
        header.magic = 'CIDL'

        obj_pt = ObjectPointer()
        obj_pt.length = ((32+16) * len(tracks)) + 16
        obj_pt.offset = 0x20

        obj = Object()
        obj.track_cnt = len(tracks)
        obj.track_sz = 32 + 16
        obj.padding = struct.pack('<2I', 0, 0)

        padding = bytearray()
        padding_blk1 = bytearray([0,0,0,0,0x1, 0xf, 0x50, 0x00, 0x00, 0x4, 0,0,0,0x1, 0x2, 0x3])
        padding_blk2 = bytearray([0xc8, 0xd8, 0x36, 0xd8, 0x11, 0x22, 0x33, 0x44]) + bytearray([0] * 24)

        for i in range(0, len(tracks)):
            padding += (padding_blk1 + padding_blk2)
        
        all_blk = header.tobytes() + obj_pt.tobytes() + obj.tobytes() + padding

        filepath = '%s/%s' % (self.audio_path, '05CIDLST.DAT')
        f = open(filepath, 'wb+')
        if f is None:
            print('Failed open %s' % filepath)
            return
        f.write(all_blk)
        f.close()


    def sync_tracks(self, tracks):
        idx = 1
        track_cnt = len(tracks)
        for i in tqdm(range(track_cnt)):
            track = tracks[i]
            print(track.filename)

            dir_name = '%s/10F%02x' % (self.audio_path, (idx >> 8))
            track.oma_name = '1%07x.OMA' % idx

            if not isdir(dir_name):
                mkdir(dir_name)
            track.generate_oma(dir_name)

            idx = idx + 1

    def get_artist_list(self, tracks):
        artists = []
        for track in tracks:
            if track.tags['author'].val not in artists:
                artists.append(track.tags['author'].val)
        artists.sort()
        return artists


    def get_album_list(self, tracks):
        albums = []
        for track in tracks:
            if track.tags['album'].val not in albums:
                albums.append(track.tags['album'].val)
        albums.sort()
        return albums


    def get_genre_list(self, tracks):
        genres = []
        for track in tracks:
            if track.tags['genre'].val not in genres:
                genres.append(track.tags['genre'].val)
        genres.sort()
        return genres


    def sort_track(self, anylist, tracks, attr):
        tracks_lst = [[] for i in range(len(anylist))]

        for track in tracks:
            for idx, ele in enumerate(anylist):
                track_attr = track.tags[attr].val
                if track_attr == ele:
                    break
            tracks_lst[idx].append(track)

        for tracks in tracks_lst:
            tracks.sort(key=lambda x : x.track_id)

        sorted_tracks = [track for tracks in tracks_lst for track in tracks]
        return sorted_tracks  
