class PubInfo():
    def __init__(self, item_id, mac_address, nlri, label, next_hop, encapsulations):
        self.item_id = item_id
        self.mac_address = mac_address
        self.nlri = nlri
        self.next_hop = next_hop
        self.label = label
        self.encapsulations = encapsulations


class Event(object):
    pass


class Observable(object):
    def __init__(self):
        self.callbacks = []
    def add_callback(self, callback):
        self.callbacks.append(callback)
    def fire(self, **attrs):
        e = Event()
        e.source = self
        for k, v in attrs.iteritems():
            setattr(e, k, v)
        for fn in self.callbacks:
            fn(e)