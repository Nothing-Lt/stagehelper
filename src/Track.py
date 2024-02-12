import struct

from os import path

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3 as id3

from Tag import *
from sonypy_var import *

class Track():
    def __init__(self, audiofile=None):
        # set the common info
        self.ftype = bytearray([0, 0, 0xff, 0xff])
        self.encoding = 0
        self.tag_len = 5
        self.tag_sz = 128
        self.oma_name = ''
        self.tags = dict()
        self.sync = False
        # set the audio based info
        if audiofile is None:
            self.time_len = 0
            self.title = ''
            self.author = ''
            self.album = ''
            self.genre = ''
            self.oma_name = ''
            self.filename = ''
            self.track_id = 0
        else:
            self.filename = audiofile
            self.fill_info_by_audio(audiofile)
            self.oma_name = ''

    # def fill_info_by_track(self, track_id, bytestream):
    #     self.track_id = track_id
    #     self.ftype = bytestream[0:4]
    #     self.encoding = struct.unpack('>I', bytestream[4:8])[0]
    #     self.time_len = int(struct.unpack('>I', bytestream[8:12])[0] / 1000)
    #     self.tag_len = struct.unpack('>H', bytestream[12:14])[0]
    #     self.tag_sz = struct.unpack('>H', bytestream[14:16])[0]

    # def fill_info_by_tags(self, bytestream):        
    #     # decode bytestream
    #     tag = Tag()
    #     tag.type = bytestream[0:4].decode('utf-8')
    #     tag.encoding = bytestream[4:6]
    #     tag.val = bytestream[6:].decode('utf-8', "ignore")
    #     self.tags[tag_type] = tag


    def fill_info_by_audio(self, filename):
        self.filename = filename
        audio_tags = id3(filename)

        # get the title
        tag = Tag()
        tag.type = bytes('TIT2', 'utf-8')[0:4]
        try:
            tag.val = audio_tags['title'][0]
        except KeyError:
           tag.val = path.basename(filename)
        self.tags['title'] = tag

        # get album
        tag = Tag()
        tag.type = bytes('TALB', 'utf-8')[0:4]
        try:
            tag.val = audio_tags['album'][0]
        except KeyError:
            tag.val = 'Unknown'
        self.tags['album'] = tag

        # get time length
        try:
            self.time_len = int(audio_tags['length'][0])
        except Exception:
            self.time_len = 0

        if self.time_len == 0:
            au_tmp = MP3(filename)
            self.time_len = au_tmp.info.length

        # get track number
        try:
            self.track_id = audio_tags['tracknumber'][0]
        except KeyError:
            self.track_id = 1

        # get author
        tag = Tag()
        tag.type = bytes('TPE1', 'utf-8')[0:4]
        try:
            tag.val = audio_tags['author'][0]
        except KeyError:
            tag.val = 'Unknown'
        self.tags['author'] = tag

        # get genre
        tag = Tag()
        tag.type = bytes('TCON', 'utf-8')[0:4]
        try:
            tag.val = audio_tags['genre'][0]
        except KeyError:
            tag.val = 'Blue'
        self.tags['genre'] = tag

        # get date
        try:
            self.date = audio_tags['date'][0]
        except KeyError:
            self.date = '2001/01/01'

        tag = Tag()
        tag.type = bytes('TSOP', 'utf-8')[0:4]
        self.tags['tsop'] = tag

    def generate_oma(self, target_path):
        if not path.isdir(target_path):
            print(target_path)
            return
    
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

        audio_header = bytestream[0:10]
        audio_tag = str(audio_header[0:3].decode('utf-8'))
        if audio_tag == 'ID3': 
            start_point = (int(audio_header[6]) << 21) + \
                        (int(audio_header[7]) << 14) + \
                        (int(audio_header[8]) << 7) + \
                        int(audio_header[9]) + 10
        else:
            start_point = 0

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

        if (((mpeg_ver * 3) + sample_rate_idx) >= 12) or (((mpeg_ver * 3) + layer_ver) >= 16):
            frame_cnt = 0
        else:
            sample_rate = SAMPLE_RATE[(mpeg_ver*3)+sample_rate_idx]
            sample_perframe = SAMPLE_PER_FRAME[(mpeg_ver*4)+layer_ver]
            frame_cnt = int((self.time_len * sample_rate) / sample_perframe)

        # skip frame header
        vbr_tag = bytestream[start_point+36:start_point+40]
        vbr_tag = vbr_tag.decode('utf-8', "ignore")
        # print(vbr_tag)
        is_vbr = False
        if vbr_tag == 'XING':
            is_vbr = True

        # start to generate oma file
        idv2_header = bytes('ea3', 'utf-8')[0:3] + bytearray([3,0,0,0,0,0x17,0x76])

        # tit2 limit the title to be 32-byte, consider unicode 16-char
        title_header = bytes('TIT2','utf-8')[0:4] + struct.pack('>I', 32) + bytearray([0,0,2])
        title_var = bytes(self.tags['title'].val, 'utf-8')[0:16] 
        title_var = title_var + bytearray([0] * (32-len(title_var)))

        # artist tag, same as tit2
        artist_header = bytes('TPE1', 'utf-8')[0:4] + struct.pack('>I', 32) + bytearray([0,0,2])
        artist_var = bytes(self.tags['author'].val, 'utf-8')[0:16]
        artist_var = artist_var + bytearray([0] * (32-len(artist_var)))

        # album tag, same as tit2
        album_header = bytes('TALB', 'utf-8')[0:4] + struct.pack('>I', 32) + bytearray([0,0,2])
        album_var = bytes(self.tags['album'].val, 'utf-8')[0:16]
        album_var = album_var + bytearray([0] * (32-len(album_var)))

        # genre tag
        genre_header = bytes('TCON', 'utf-8')[0:4] + struct.pack('>I', 32) + bytearray([0,0,2])
        genre_var = bytes(self.tags['genre'].val, 'utf-8')[0:16]
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
        third_header = third_header + struct.pack('>I', int(self.time_len * 1000))
        third_header = third_header + struct.pack('>I', frame_cnt)
        third_header = third_header + bytearray([0,0,0,0])
        padding = bytearray([0] * 48)

        oma_data = oma_header + second_header + second_var + third_header + padding

        # just copy, will do no encoding or decoding things
        audio_data = bytestream[start_point:]

        fout = open(target_path+ '/' + self.oma_name, 'wb+')
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
        self.tag_len = len(self.tags)
        blk =  self.ftype + \
            struct.pack('>2I2H', self.encoding, int((self.time_len * 1000)), self.tag_len, self.tag_sz)

        return blk
    # def tobytes(self)

    def tags_to_bytes(self):
        tags_blk = self.tags['title'].tobytes(self.tag_sz)
        tags_blk += self.tags['author'].tobytes(self.tag_sz)
        tags_blk += self.tags['album'].tobytes(self.tag_sz)
        tags_blk += self.tags['genre'].tobytes(self.tag_sz)
        tags_blk += self.tags['tsop'].tobytes(self.tag_sz)
        return tags_blk
