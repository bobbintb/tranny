from time import time
from collections import namedtuple

TorrentData = namedtuple("TorrentData", ['release_name', "torrent_data", "section"])


class Release(object):
    def __init__(self, release_name):
        self.release_name = release_name
        self.creation_time = time()
        self.start_time = None
        self.finish_time = None
