from time import time, sleep
from logging import getLogger
from tranny.configuration import Configuration
from tranny.rss import RSSFeed
from tranny import db

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
        db.init_db()
        self.feeds = [RSSFeed(**feed) for feed in config.rss_feeds]

    def run_forever(self):
        running = True
        while running:
            for feed in self.feeds:
                try:
                    for release in feed.find_matches():
                        self.log.info("Matched release: {0}".format(release))
                except Exception as err:
                    self.log.exception("Error updated feed", err)

