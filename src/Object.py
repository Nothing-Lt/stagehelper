import struct

from Track import Track

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
            self.track_sz = (128 * 5) + 16 # (track header + sizeof(all tags))
        
        self.padding = bytearray([0] * 8)
        self.tracks = []

    def add_track(self, new_track):
        if isinstance(new_track, Track):
            self.tracks.append(new_track)
            self.track_cnt = len(self.tracks)

    def tobytes(self):
        return bytes(self.magic, 'utf-8')[0:4] + \
                struct.pack('>2H', self.track_cnt, self.track_sz) + self.padding
