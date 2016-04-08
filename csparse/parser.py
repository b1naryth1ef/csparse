import struct
from collections import defaultdict

from .proto.netmessages_pb2 import *
from .demo import DemoMsg
from .event import GameEventDesc


def get_net_msg_mapping():
    """
    Returns a mapping of NET_Msg CMD ID's to the NET_Msg struct
    """
    for name, index in NET_Messages.items():
        yield (index, globals().get('CNETMsg_%s' % name.split('_', 1)[-1], None))


def get_svc_msg_mapping():
    """
    Returns a mapping of SVC_Msg CMD ID's to the SVC_Msg struct
    """
    for name, index in SVC_Messages.items():
        yield (index, globals().get('CSVCMsg_%s' % name.split('_', 1)[-1], None))


class DemoParser(object):
    NET_MSG_MAPPING = dict(get_net_msg_mapping())
    SVC_MSG_MAPPING = dict(get_svc_msg_mapping())

    def __init__(self, demo):
        self.demo = demo

        # Mapping of game events loaded from CSVCMsg_GameEventList event
        self.game_events = {}

        # Handles internal, unmodified events
        self.internal_event_handlers = defaultdict(list)

        # Handle game events, these are structured by the library
        self.game_event_handlers = defaultdict(list)

    def on(self, event_type, callback):
        if isinstance(event_type, int):
            self.internal_event_handlers[event_type].append(callback)
        else:
            self.game_event_handlers[event_type].append(callback)

    def parse(self):
        events = 0

        while True:
            cmd, tick, slot = self.demo.read_cmd_header()
            events += 1

            if cmd == DemoMsg.SIGNON or cmd == DemoMsg.PACKET:
                self.handle_demo_packet()
            elif cmd in (DemoMsg.CONSOLECMD, DemoMsg.DATATABLES, DemoMsg.STRINGTABLES):
                self.demo.read_raw_data()
            elif cmd == DemoMsg.USERCMD:
                self.demo.read_user_cmd()
            elif cmd == DemoMsg.SYNCTICK:
                continue
            elif cmd == DemoMsg.STOP:
                break

        return events

    def handle_netmsg(self, msg, data):
        obj = self.NET_MSG_MAPPING[msg]()
        obj.ParseFromString(data)

        if msg in self.internal_event_handlers:
            map(lambda i: i(msg, data), self.internal_event_handlers[msg])

    def handle_svcmsg(self, msg, data):
        obj = self.SVC_MSG_MAPPING[msg]()
        obj.ParseFromString(data)

        if msg == svc_GameEvent:
            self.handle_game_event(obj)

        if msg == svc_GameEventList:
            self.handle_game_event_list(obj)

        if msg in self.internal_event_handlers:
            map(lambda i: i(msg, data), self.internal_event_handlers[msg])

    def handle_game_event(self, event):
        desc = self.game_events[event.eventid]

        if not len(self.game_event_handlers[desc.name]):
            return

        obj = desc.from_event(event)
        for handler in self.game_event_handlers[desc.name]:
            handler(obj)

    def handle_game_event_list(self, event):
        for desc in event.descriptors:
            self.game_events[desc.eventid] = GameEventDesc(desc)

    def handle_demo_packet(self):
        self.demo.read_cmd_info()
        self.demo.read_sequence_info()

        size, buf = self.demo.read_raw_data()
        if size > 0:
            self.parse_packet(buf, size)

    def parse_packet(self, buf, size):
        index = 0

        while index < size:
            cmd, index = self.read_int32(buf, index)
            cmd_size, index = self.read_int32(buf, index)
            data = buf[index: index + cmd_size]

            if cmd in NET_Messages.values():
                self.handle_netmsg(cmd, data)

            if cmd in SVC_Messages.values():
                self.handle_svcmsg(cmd, data)

            index += cmd_size

    def read_int32(self, buf, index):
        '''
        Reads an int32 from a binary buffer.
        '''
        b = 0
        count = 0
        result = 0

        cont = True
        while cont:
            if count == 5:
                return result
            b = struct.unpack_from("B", buf, index)
            b = b[0]
            index = index + 1
            result |= (b & 0x7F) << (7 * count)
            count = count + 1
            cont = b & 0x80
        return result, index

    def _read_int32(self, buf, index):
        count, result = 0, 0

        while True:
            byte = struct.unpack_from('@B', buf, index)[0]
            index += 1
            result |= (byte & 0x7F) << (7 * count)
            count += 1
            if not byte & 0x80 or count == 5:
                break

        return result, index
