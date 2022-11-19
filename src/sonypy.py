
import struct

from sonypy_var import *

# Define 04CNTINF.DAT's header






class Track():
    def __init__(self):
        self.ftype = bytearray([0, 0, 0xff, 0xff])
        self.encoding = 0
        self.time_len = 0
        self.title = ''
        self.author = ''
        self.album = ''
        self.genre = ''
        self.tag_len = 0
        self.tag_sz = 128
        self.oma_name = ''
        self.filename = ''
        self.track_id = 0
        self.sync = False
    # def __init__(self, bytestream=None)

    def fill_in_track(self, track_id, bytestream):
        self.track_id = track_id
        self.ftype = bytestream[0:4]
        self.encoding = struct.unpack('>I', bytestream[4:8])[0]
        self.time_len = int(struct.unpack('>I', bytestream[8:12])[0] / 1000)
        self.tag_len = struct.unpack('>H', bytestream[12:14])[0]
        self.tag_sz = struct.unpack('>H', bytestream[14:16])[0]

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

    def set_by_audio(self, filename):
        f = open(filename, 'rb')
        if f is None:
            return

        self.filename = filename
        bytestream = f.read()
        if len(bytestream) < 10:
            f.close()
            return

        # print(bytestream)
        audio_header = bytestream[0:10]
        audio_tag = str(audio_header[0:3].decode('utf-8'))
        if audio_tag == 'ID3': 
            start_point = (int(audio_header[6]) << 21) + \
                        (int(audio_header[7]) << 14) + \
                        (int(audio_header[8]) << 7) + \
                        int(audio_header[9]) + 10
        else:
            start_point = 0
        print(audio_tag)
        print(start_point)

        # skip 0s
        while True:
            if bytestream[start_point] != 0:
                break;
            start_point += 1  

        if bytestream[start_point] != 0xff:
            print('Not a valid file format')
            f.close()
            return
        # go parse the info from audio file
        mpeg_head = bytestream[start_point+1:start_point+4]
        if mpeg_head[0] & 0xe0 != 0xe0:
            print('invalid encoding')
            f.close()
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

        # skip frame header
        vbr_tag = bytestream[start_point+36:start_point+40]
        vbr_tag = vbr_tag.decode('utf-8', "ignore")
        print(vbr_tag)
        is_vbr = False
        if vbr_tag == 'XING':
            is_vbr = True

        f.close()
        # TODO : a lot ...

    def generate_oma(self, target_path):
        if len(self.oma_name) <=0 :
            print('generate %s, but has no oma name' % self.filename)
            return

        fin = open(self.filename, 'rb')
        if fin is None:
            print('cannot find %s', self.filename)
            return

        bytestream = fin.read()
        if len(bytestream) < 10:
            fin.close()
            return

        # print(bytestream)
        audio_header = bytestream[0:10]
        audio_tag = str(audio_header[0:3].decode('utf-8'))
        if audio_tag == 'ID3': 
            start_point = (int(audio_header[6]) << 21) + \
                        (int(audio_header[7]) << 14) + \
                        (int(audio_header[8]) << 7) + \
                        int(audio_header[9]) + 10
        else:
            start_point = 0
        print(audio_tag)
        print(start_point)

        # skip 0s
        while True:
            if bytestream[start_point] != 0:
                break;
            start_point += 1  

        if bytestream[start_point] != 0xff:
            print('Not a valid file format')
            f.close()
            return
        # go parse the info from audio file
        mpeg_head = bytestream[start_point+1:start_point+4]
        if mpeg_head[0] & 0xe0 != 0xe0:
            print('invalid encoding')
            f.close()
            return

        self.encoding = ((mpeg_head[0] & 0x1e) << 3) + \
                        ((mpeg_head[1] & 0xf0) >> 4)
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
            frame_cnt = int((self.time_len * sample_rate) / sample_perframe)
        print(sample_rate)
        print(sample_perframe)
        print(frame_cnt)

        # skip frame header
        vbr_tag = bytestream[start_point+36:start_point+40]
        vbr_tag = vbr_tag.decode('utf-8', "ignore")
        print(vbr_tag)
        is_vbr = False
        if vbr_tag == 'XING':
            is_vbr = True

        # start to generate oma file
        idv2_header = bytes('ea3', 'utf-8')[0:3] + bytearray([3,0,0,0,0,0x17,0x76])

        # tit2 limit the title to be 32-byte, consider unicode 16-char
        title_header = bytes('TIT2','utf-8')[0:4] + struct.pack('>I', 32) + bytearray([0,0,2])
        title_var = bytes(self.title, 'utf-8')[0:16] 
        title_var = title_var + bytearray([0] * (32-len(title_var)))

        # artist tag, same as tit2
        artist_header = bytes('TPE1', 'utf-8')[0:4] + struct.pack('>I', 32) + bytearray([0,0,2])
        artist_var = bytes(self.author, 'utf-8')[0:16]
        artist_var = artist_var + bytearray([0] * (32-len(artist_var)))

        # album tag, same as tit2
        album_header = bytes('TALB', 'utf-8')[0:4] + struct.pack('>I', 32) + bytearray([0,0,2])
        album_var = bytes(self.album, 'utf-8')[0:16]
        album_var = album_var + bytearray([0] * (32-len(album_var)))

        # genre tag
        genre_header = bytes('TCON', 'utf-8')[0:4] + struct.pack('>I', 32) + bytearray([0,0,2])
        genre_var = bytes(self.genre, 'utf-8')[0:16]
        genre_var = genre_var + bytearray([0] * (32-len(genre_var)))

        # track number tag
        track_nr_header = bytes('TXXX', 'utf-8')[0:4] + struct.pack('>I', 32) + bytearray([0,0,2])
        track_nr_var = bytes('OMG_TRACK ','utf-8')[0:10] + struct.pack('H', self.track_id)
        track_nr_var = track_nr_var + bytearray([0] * (32-len(track_nr_var)))

        # transfer date tag
        date_header = bytes('TXXX','utf-8')[0:4] + struct.pack('>I', 32) + bytearray([0,0,2])
        date_var = bytes('OMG_TRLDA 2001/01/01 00:00:00', 'utf-8')
        date_var = date_var + bytearray([0] * (32-len(date_var)))

        # track len tag
        track_len_head = bytes('TLEN','utf-8')[0:4] + struct.pack('>I', 32) + bytearray([0,0,2])
        track_len_var = bytes(('%d' % (self.time_len * 1000)), 'utf-8')
        track_len_var = track_len_var + bytearray([0] * (32-len(track_len_var)))

        # assemble to have a oma_header
        oma_header = idv2_header + \
                    title_header + title_var + \
                    artist_header + artist_var + \
                    album_header + album_var + \
                    genre_header + genre_var + \
                    track_nr_header + track_nr_var + \
                    date_header + date_var + \
                    track_len_head + track_len_var
        oma_header = oma_header + bytearray([0] * (3072-len(oma_header)))

        second_header = bytes('EA3', 'utf-8')[0:3] + bytearray([2, 0, 0x60, 0xff, 0xff, 0, 0, 0, 0, 1, 0xf, 0x50, 0])
        second_var = bytearray([0, 4, 0, 0, 0, 1, 2, 3, 0xc8, 0xd8, 0x36, 0xd8, 0x11, 0x22, 0x33 ,0x44])

        third_header = bytearray([3])
        if is_vbr:
            third_header = third_header + bytearray([0x90])
        else:
            third_header = third_header + bytearray([0x80])
        third_header = third_header + bytearray([self.encoding])
        third_header = third_header + bytearray([0x10])
        third_header = third_header + struct.pack('>I', self.time_len * 1000)
        third_header = third_header + struct.pack('>I', frame_cnt)
        third_header = third_header + bytearray([0,0,0,0])
        padding = bytearray([0] * 48)

        oma_data = oma_header + second_header + second_var + third_header + padding

        # just copy, will do no encoding or decoding things
        audio_data = bytestream[start_point:]

        fout = open(self.oma_name, 'wb+')
        if fout is None:
            print('Failed in open/create %s' % self.oma_name)
            fin.close()
            return

        fout.write(oma_data + audio_data)
        fout.close()
        fin.close()

    def set_by_oma(self, oma_name):
        self.oma_name = oma_name
        return

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