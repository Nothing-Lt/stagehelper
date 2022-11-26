
import struct

from sonypy_var import *
from Header import *
from ObjectPointer import *
from Object import *
from Track import *

class Database():
    def __init__(self):
        return


    def write_00GTRLST(self, target_path):
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

        filepath = '%s/%s' % (target_path, '00GTRLST.DAT') 
        f = open(filepath, 'wb+')
        if f is None:
            print('Cannot get file %s' % filepath)
            return
        f.write(header.tobytes() + obj_pt1.tobytes() + obj_pt2.tobytes() + obj1.tobytes() + obj1_blk + obj2.tobytes() + blk_data)
        f.close()


    def write_03GINF22(self, target_path):
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

        filepath = '%s/%s' % (target_path, '03GINF22.DAT') 
        f = open(filepath, 'wb+')
        if f is None:
            print('Cannot get file %s' % filepath)
            return
        f.write(header.tobytes() + obj_pt.tobytes() + obj.tobytes())
        f.close()


    def write_01TREEXX(self, cat, tracks, id, target_path):
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
        obj.count = cat_cnt
        obj.size = 8
        obj.padding[0] = obj.count
        obj.padding[1] = 0

        # id 1 and 3 for album, 2 for artist, 4 for genre

        return None


    def get_artist_list(self, tracks):
        artists = []
        for track in tracks:
            if track.author not in artists:
                artists.append(track.author)
        artists.sort()
        return artists


    def get_album_list(self, tracks):
        albums = []
        for track in tracks:
            if track.album not in albums:
                albums.append(track.album)
        albums.sort()
        return albums


    def get_genre_list(self, tracks):
        genres = []
        for track in tracks:
            if track.genre not in genres:
                genres.append(track.genre)
        genres.sort()
        return genres


    def sort_track(self, anylist, tracks, attr):
        tracks_lst = [[] for i in range(len(anylist))]

        for track in tracks:
            for idx, ele in enumerate(anylist):
                track_attr = str(getattr(track, attr))
                if track_attr == ele:
                    break
            tracks_lst[idx].append(track)

        for tracks in tracks_lst:
            tracks.sort(key=lambda x : x.track_id)

        sorted_tracks = [track for tracks in tracks_lst for track in tracks]
        return sorted_tracks  
