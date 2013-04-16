"""
Basic in-memory volatile data store
"""
from logging import getLogger
from time import time


class MemoryStore(dict):
    def __init__(self, **kwargs):
        super(MemoryStore, self).__init__(**kwargs)
        self.log = getLogger("db.mem")

    def add(self, release_name, section=None, source=None, timestamp=None):
        if not timestamp:
            timestamp = time()
        self[release_name] = {
            'ctime': timestamp,
            'section': section,
            'source': source
        }

    def size(self):
        return len(self)

    def sync(self):
        return True
