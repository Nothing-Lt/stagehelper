
import struct


# Define 04CNTINF.DAT's header
class Header():
    def __init__(self):
        self.magic = ''
        self.CTE = None
        self.op_cnt = 0 # amount of object pointer

    def __init__(self, bytestream):
        self.magic = (bytestream[0:4]).decode('utf-8')
        self.CTE = bytestream[4:8] # constant number
        self.op_cnt = bytestream[8]

    def tobytes(self):
        bytes(self.magic, 'utf-8')
        return bytes(self.magic, 'utf-8') + \
                self.CTE + \
                struct.pack('8B', self.op_cnt, 0, 0, 0, 0, 0, 0, 0)


# Define object pointer
class ObjectPointer():
    def __init__(self):
        self.magic = ''
        self.offset = 0
        self.length = 0

    def __init__(self, bytestream):
        self.magic = (bytestream[0:4]).decode('utf-8')
        self.offset = struct.unpack('>I', bytestream[4:8])[0]
        self.length = struct.unpack('>I', bytestream[8:12])[0]

    def tobytes(self):
        return bytes(self.magic, 'utf-8') + \
                struct.pack('>3I', self.offset, self.length, 0)


# Define object
class Object():
    def __init__(self):
        self.magic = ''
        self.track_cnt = 0 # amount of record
        self.track_sz = 0 # size of track 

    def __init__(self, bytestream):
        self.magic = (bytestream[0:4]).decode('utf-8')
        self.track_cnt = struct.unpack('>H', bytestream[4:6])[0]
        self.track_sz = struct.unpack('>H', bytestream[6:8])[0]

    def tobytes(self):
        return bytes(self.magic, 'utf-8') + \
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

    def __init__(self, bytestream):
        self.ftype = bytestream[0:4]
        self.encoding = struct.unpack('>I', bytestream[4:8])[0]
        self.time_len = struct.unpack('>I', bytestream[8:12])[0] / 1000
        self.tag_len = struct.unpack('>H', bytestream[12:14])[0]
        self.tag_sz = struct.unpack('>H', bytestream[14:16])[0]


    def fill_in_tags(self, bytestream):
        
        # decode bytestream
        tag_type = bytestream[0:4].decode('utf-8')
        tag_encoding = bytestream[4:5]
        tag_val = bytestream[5:].decode('utf-8', "ignore")

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

    def __str__(self):
        return 'ftype:'+ str(self.ftype) + ', ' + \
                'encoding:' + str(self.encoding)+ ', ' + \
                'time_len:' + str(self.time_len) + ', ' + \
                'title:' + self.title + ', ' + \
                'author:' + self.author + ', ' + \
                'album:' + self.album + ', ' + \
                'genre:' + self.genre

    def tobytes(self):
        bytestream = struct.pack()
        return bytestream
