
class Tag:
    def __init__(self):
        self.type = bytearray([0,0,0,0])
        self.encoding = struct.pack('>2H', 2)
        self.val = bytearray([0])
        return

    def tobytes(self, tag_sz):
        blk = self.type + self.encoding + self.val
        padding_sz = tag_sz - len(blk)
        for j in range(0, padding_sz):
            blk += bytes([0])
        return blk
