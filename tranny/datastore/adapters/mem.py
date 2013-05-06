"""
Basic in-memory volatile data store
"""
from logging import getLogger
from time import time
from tranny.datastore import Datastore


class MemoryStore(Datastore, dict):
    def __init__(self, **kwargs):
        super(MemoryStore, self).__init__(**kwargs)
        self.log = getLogger("db.mem")

    def add(self, release_key, release_name, section=None, source=None, timestamp=None):
        if not timestamp:
            timestamp = time()
        self[release_key] = {
            'ctime': timestamp,
            'release_key': release_key,
            'release_name': release_name,
            'section': section,
            'source': source
        }
        self.log.debug("Added key to the mem datastore: {0}".format(release_key))

    def size(self):
        return len(self)

    def sync(self):
        return True

    def fetch(self, limit=25):
        releases = sorted(self.values(), cmp=lambda h: h['timestamp'], reverse=True)
        if limit:
            return releases[0:25]
        return releases
