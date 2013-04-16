"""
A shelve / pickle backed datastore for release history
"""
from logging import getLogger
from shelve import DbfilenameShelf
from time import time
from tranny import config


class GherkinStore(DbfilenameShelf):
    def __init__(self, filename=None, flag='c', protocol=None, writeback=False):
        if not filename:
            filename = config.get_db_path()
        DbfilenameShelf.__init__(self, filename, flag, protocol, writeback)
        self.log = log = getLogger("db.gherkin")

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
