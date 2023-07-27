import struct

class Tag:
    def __init__(self):
        self.type = bytearray([0,0,0,0])
        self.encoding = struct.pack('>H', 2)
        self.val = ''

    def tobytes(self, tag_sz):
        blk = self.type + self.encoding + bytes(self.val, 'utf-8')
        blk = blk[0:tag_sz]
        padding_sz = tag_sz - len(blk)
        for j in range(0, padding_sz):
            blk += bytes([0])
        return blk
