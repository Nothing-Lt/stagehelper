import struct

# Define object pointer
class ObjectPointer():
    def __init__(self, bytestream=None):
        if bytestream is not None:
            self.magic = (bytestream[0:4]).decode('utf-8')
            self.offset = struct.unpack('<I', bytestream[4:8])[0]
            self.length = struct.unpack('<I', bytestream[8:12])[0]
        else:
            self.magic = 'CNFB'
            self.offset = 32
            self.length = 1328

    def tobytes(self):
        return bytes(self.magic, 'utf-8')[0:4] + \
                struct.pack('>3I', self.offset, self.length, 0)
