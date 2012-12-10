from time import time

class Release(object):
    def __init__(self, release_name):
        self.release_name = release_name
        self.creation_time = time()
        self.start_time = None
        self.finish_time = None

