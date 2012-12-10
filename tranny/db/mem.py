from logging import getLogger
from time import time
from pickle import dumps, load

class MemDB(object):
    def __init__(self, db_path="tranny.db"):
        self.log = getLogger("tranny.db.pickle")
        self.log.info("Started PickleDB Datastore")
        self.db_path = db_path
        try:
            self.db = load(db_path)
        except OSError:
            self.db = {}

    def add(self, release_name, section=None, source=None, timestamp=None):
        if not timestamp:
            timestamp = time()
        self.db[release_name] = {
            'ctime': timestamp,
            'section': section,
            'source': source
        }


    def exists(self, release):
        return

    def remove(self):
        pass

    def size(self):
        pass

    def fetch(self):
        pass

    def sync(self):
        pass
