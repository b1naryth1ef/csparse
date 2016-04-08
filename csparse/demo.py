from holster.enum import Enum

import struct

class InvalidDemoError(Exception):
    pass

DemoMsg = Enum('null',
    'signon',
    'packet',
    'synctick',
    'consolecmd',
    'usercmd',
    'datatables',
    'stop',
    'customdata',
    'stringtables')

class DemoHeader(object):
    MAX_OS_PATH = 260
    FORMAT = '@8sii{0}s{0}s{0}s{0}sfiii'.format(MAX_OS_PATH)

    def __init__(self, timestamp, demo_protocol, net_protocol,
            server_name, client_name, map_name, game_dir, playback_time,
            playback_ticks, playback_frames, signon_length):
        self.timestamp = timestamp
        self.demo_protocol = demo_protocol
        self.net_protocol = net_protocol
        self.server_name = server_name
        self.client_name = client_name
        self.map_name = map_name
        self.game_dir = game_dir
        self.playback_time = playback_time
        self.playback_ticks = playback_ticks
        self.playback_frames = playback_frames
        self.signon_length = signon_length

    @classmethod
    def from_file(cls, f):
        raw_data = struct.unpack(cls.FORMAT, f.read(struct.calcsize(cls.FORMAT)))
        return cls(*raw_data)

class DemoFile(object):
    DEMO_PROTOCOL_VERSION = 4

    def __init__(self, f):
        self.f = f
        self.header = DemoHeader.from_file(f)

        if self.header.demo_protocol != self.DEMO_PROTOCOL_VERSION:
            raise InvalidDemoError("Invalid demo protocol {}".format(self.DEMO_PROTOCOL_VERSION))

    def read_struct(self, fmt):
        return struct.unpack(fmt, self.f.read(struct.calcsize(fmt)))[0]

    def read_cmd_header(self):
        cmd = self.read_struct('@B')

        if cmd <= 0:
            return DemoMsg.STOP, 0, 0

        tick = self.read_struct('@i')
        slot = self.read_struct('@B')

        return cmd, tick, slot

    def read_raw_data(self):
        size = self.read_struct('@i')
        data = self.f.read(size)
        return size, data

    def read_user_cmd(self):
        seq = self.read_struct('@i')
        size, data = self.read_raw_data()
        return seq, size, data

    def read_cmd_info(self):
        fmt = '@{}'.format('iffffffffffffffffff' * 2)
        return self.read_struct(fmt)

    def read_sequence_info(self):
        seq_in = self.read_struct('@i')
        seq_out = self.read_struct('@i')
        return seq_in, seq_out
