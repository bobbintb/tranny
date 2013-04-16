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
        self.log = getLogger("db.gherkin")

    def add(self, release_key, section=None, source=None, timestamp=None):
        if not timestamp:
            timestamp = time()

        self[release_key] = {
            'ctime': timestamp,
            'section': section,
            'source': source
        }
        self.log.debug("Added key to the gherkin datastore: {0}".format(release_key))

    def size(self):
        return len(self)
