from time import time, sleep
from logging import getLogger
from tranny.confinguration import Configuration
from tranny.rss import RSSFeed

config = None
if not config:
    config = Configuration()
    config.initialize()

# Current run state
running = False

class Tranny:
    feeds = []

    def __init__(self, wait_time=1):
        self.wait_time = wait_time
        self.log = getLogger("tranny.main")
        self.log.info("Tranny initializing")


    def init(self):
        self.feeds = [RSSFeed(**feed) for feed in config.rss_feeds]

    def run_forever(self):
        running = True
        while running:
            for feed in self.feeds:
                try:
                    was_updated = feed.update()
                except Exception as err:
                    self.log.exception("Error updated feed", err)
