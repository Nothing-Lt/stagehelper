
import struct

from sonypy_var import *

# Define 04CNTINF.DAT's header
class Header():
    def __init__(self):
        self.magic = ''
        self.CTE = 0
        self.op_cnt = 0 # amount of object pointer

    def __init__(self, bytestream=None):
        if bytestream is not None:
            self.magic = (bytestream[0:4]).decode('utf-8')
            self.CTE = bytestream[4:8] # constant number
            self.op_cnt = bytestream[8]
        else:
            self.magic = 'CNIF'
            self.CTE = struct.pack('I', 257)
            self.op_cnt = 1 # amount of object pointer

    def tobytes(self):
        return bytes(self.magic, 'utf-8')[0:4] + \
                self.CTE + \
                struct.pack('8B', self.op_cnt, 0, 0, 0, 0, 0, 0, 0)


# Define object pointer
class ObjectPointer():
    def __init__(self):
        self.magic = 'CNFB'
        self.offset = 32
        self.length = 1328

    def __init__(self, bytestream=None):
        if bytestream is not None:
            self.magic = (bytestream[0:4]).decode('utf-8')
            self.offset = struct.unpack('>I', bytestream[4:8])[0]
            self.length = struct.unpack('>I', bytestream[8:12])[0]
        else:
            self.magic = 'CNFB'
            self.offset = 32
            self.length = 1328

    def tobytes(self):
        return bytes(self.magic, 'utf-8')[0:4] + \
                struct.pack('>3I', self.offset, self.length, 0)


# Define object
class Object():
    def __init__(self):
        self.magic = 'CNFB'
        self.track_cnt = 0 # amount of record
        self.track_sz = 0 # size of track 

    def __init__(self, bytestream=None):
        if bytestream is not None:
            self.magic = (bytestream[0:4]).decode('utf-8')
            self.track_cnt = struct.unpack('>H', bytestream[4:6])[0]
            self.track_sz = struct.unpack('>H', bytestream[6:8])[0]
        else:
            self.magic = 'CNFB'
            self.track_cnt = 0 # amount of record
            self.track_sz = 0 # size of track 

    def tobytes(self):
        return bytes(self.magic, 'utf-8')[0:4] + \
                struct.pack('>2H2I', self.track_cnt, self.track_sz, 0, 0)


# Definition of track in sony
#   encoding
#   time_len
#   title
#   author
#   album
#   genre
class Track():
    def __init__(self):
        self.ftype = None
        self.encoding = 0
        self.time_len = 0
        self.title = ''
        self.author = ''
        self.album = ''
        self.genre = ''
        self.tag_len = 0
        self.tag_sz = 0
        self.filename = ''
    # def __init__(self)

    def __init__(self, bytestream=None):
        if bytestream is not None:
            self.ftype = bytestream[0:4]
            self.encoding = struct.unpack('>I', bytestream[4:8])[0]
            self.time_len = int(struct.unpack('>I', bytestream[8:12])[0] / 1000)
            self.tag_len = struct.unpack('>H', bytestream[12:14])[0]
            self.tag_sz = struct.unpack('>H', bytestream[14:16])[0]
            self.filename = ''
        else:
            self.ftype = None
            self.encoding = 0
            self.time_len = 0
            self.title = ''
            self.author = ''
            self.album = ''
            self.genre = ''
            self.tag_len = 0
            self.tag_sz = 0
            self.filename = ''
    # def __init__(self, bytestream=None)

    def fill_in_tags(self, bytestream):        
        # decode bytestream
        tag_type = bytestream[0:4].decode('utf-8')
        tag_encoding = bytestream[4:6]
        tag_val = bytestream[6:].decode('utf-8', "ignore")

        # fill in info 
        if tag_type == 'TIT2':
            self.title = tag_val
        elif tag_type == 'TPE1':
            self.author = tag_val
        elif tag_type == 'TALB':
            self.album = tag_val
        elif tag_type == 'TCON':
            self.genre = tag_val
        else:
            return False, tag_type, tag_val
        return True, tag_type, tag_val
    # def fill_in_tags(self, bytestream)

    def bind_with_file(self, filename):
        self.filename = filename
    # def bind_with_file(self, filename)

    def load_from_audio_file(self, bytestream):
        if len(bytestream) < 10:
            return

        print(bytestream)
        audio_header = bytestream[0:10]
        audio_tag = str(audio_header[0:3].decode('utf-8'))
        if audio_tag == 'ID3': 
            start_point = (int(audio_header[6]) << 21) + \
                        (int(audio_header[7]) << 14) + \
                        (int(audio_header[8]) << 7) + \
                        int(audio_header[9]) + 10
        else:
            start_point = 0
        print(audio_header)
        print(audio_tag)
        print(start_point)

        # skip 0s
        while True:
            if bytestream[start_point] != 0:
                break;
            start_point += 1  

        if bytestream[start_point] != 0xff:
            print('Not a valid file format')
            return
        print('it is 0xff')
        # go parse the info from audio file
        mpeg_head = bytestream[start_point+1:start_point+4]
        if mpeg_head[0] & 0xe0 != 0xe0:
            print('invalid encoding')
            return

        self.encoding = ((mpeg_head[0] & 0x1e) << 3) + \
                        ((mpeg_head[1] & 0xf0) << 4)
        mpeg_ver = (mpeg_head[0] & 0x18) >> 3
        layer_ver = (mpeg_head[0] & 0x6) >> 1
        sample_rate_idx = (mpeg_head[1] & 0xc) >> 2
        print(mpeg_ver)
        print(layer_ver)
        print(sample_rate_idx)

        if (((mpeg_ver * 3) + sample_rate_idx) >= 12) or (((mpeg_ver * 3) + layer_ver) >= 16):
            frame_cnt = 0
        else:
            sample_rate = SAMPLE_RATE[(mpeg_ver*3)+sample_rate_idx]
            sample_perframe = SAMPLE_PER_FRAME[(mpeg_ver*4)+layer_ver]
            frame_cnt = (self.time_len * sample_rate) / sample_perframe
        print(sample_rate)
        print(sample_perframe)
        print(frame_cnt)
        # TODO : a lot ...

    # def load_from_audio_file(self, bytestream)

    def tobytes(self):
        # encode the track 
        self.tag_len = 5
        bytestream =  self.ftype + \
                        struct.pack('>2I2H', 
                        self.encoding, (self.time_len * 1000), 
                        self.tag_len, self.tag_sz)

        # encode each tag for this track
        # encode title
        bytestream_title = bytes('TIT2', 'utf-8')[0:4] + \
                        struct.pack('>H', 2) + \
                        bytes(self.title, 'utf-8')
        print(bytes(self.title, 'utf-8'))

        padding = self.tag_sz - len(bytestream_title)
        for j in range(0, padding):
            bytestream_title += bytes([0])
        
        # encode author
        bytestream_author = bytes('TPE1', 'utf-8')[0:4] + \
                            struct.pack('>H', 2) + \
                            bytes(self.author, 'utf-8')

        padding = self.tag_sz - len(bytestream_author)
        for j in range(0, padding):
            bytestream_author += bytes([0])

        # encode album
        bytestream_album = bytes('TALB', 'utf-8')[0:4] + \
                        struct.pack('>H', 2) + \
                        bytes(self.album, 'utf-8')

        padding = self.tag_sz - len(bytestream_album)
        for j in range(0, padding):
            bytestream_album += bytes([0])

        # encode grene
        bytestream_genre = bytes('TCON', 'utf-8')[0:4] + \
                    struct.pack('>H', 2) + \
                    bytes(self.genre, 'utf-8')

        padding = self.tag_sz - len(bytestream_genre)
        for j in range(0, padding):
            bytestream_genre += bytes([0])

        # encode TSOP
        bytestream_tsop = bytes('TSOP', 'utf-8')[0:4] + \
                        struct.pack('>H', 2)
        padding = self.tag_sz - len(bytestream_tsop)
        for j in range(0, padding):
            bytestream_tsop += bytes([0])

        bytestream += (bytestream_title + bytestream_author + bytestream_album + bytestream_genre + bytestream_tsop)
        return bytestream
    # def tobytes(self)

    def __str__(self):
        return 'ftype:'+ str(self.ftype) + ', ' + \
                'encoding:' + str(self.encoding)+ ', ' + \
                'time_len:' + str(self.time_len) + ', ' + \
                'title:' + self.title + ', ' + \
                'author:' + self.author + ', ' + \
                'album:' + self.album + ', ' + \
                'genre:' + self.genre
    # def __str__(self)