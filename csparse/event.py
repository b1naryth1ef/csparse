
TYPE_INDEX = {
    1: 'val_string',
    2: 'val_float',
    3: 'val_long',
    4: 'val_short',
    5: 'val_byte',
    6: 'val_bool',
    7: 'val_uint64',
    8: 'val_wstring'
}


class GameEvent(object):
    def __init__(self, obj):
        self.__dict__.update(obj)


class GameEventDesc(object):
    def __init__(self, desc):
        self.id = desc.eventid
        self.name = desc.name
        self.keys = desc.keys
        self.cls = type(
                str(self.name),
                (GameEvent, ),
                {i.name: None for i in self.keys})

    def from_event(self, event):
        data = {}
        for index, key in enumerate(self.keys):
            data[key.name] = getattr(event.keys[index], TYPE_INDEX[key.type])
        return self.cls(data)
