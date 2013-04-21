"""
Basic in-memory volatile data store
"""
from logging import getLogger
from time import time
from tranny.db import Datastore


class MemoryStore(Datastore, dict):
    def __init__(self, **kwargs):
        super(MemoryStore, self).__init__(**kwargs)
        self.log = getLogger("db.mem")

    def add(self, release_key, section=None, source=None, timestamp=None):
        if not timestamp:
            timestamp = time()
        self[release_key] = {
            'ctime': timestamp,
            'section': section,
            'source': source
        }
        self.log.debug("Added key to the mem datastore: {0}".format(release_key))
        self.sync()

    def size(self):
        return len(self)

    def sync(self):
        return True
