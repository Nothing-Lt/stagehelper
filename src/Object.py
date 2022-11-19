import struct

# Define object
class Object():
    def __init__(self, bytestream=None):
        if bytestream is not None:
            self.magic = (bytestream[0:4]).decode('utf-8')
            self.track_cnt = struct.unpack('<H', bytestream[4:6])[0]
            self.track_sz = struct.unpack('<H', bytestream[6:8])[0]
        else:
            self.magic = 'CNFB'
            self.track_cnt = 0 # amount of record
            self.track_sz = 0 # size of track, it is (track header + sizeof(all tags))

    def tobytes(self):
        return bytes(self.magic, 'utf-8')[0:4] + \
                struct.pack('>2H2I', self.track_cnt, self.track_sz, 0, 0)