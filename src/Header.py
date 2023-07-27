import struct

class Header():
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
