from time import time
from logging import getLogger
from feedparser import parse as parse

class RSSFeed(object):

    # Timestamp of last successful update
    last_update = 0

    def __init__(self, url, name="Unknown", interval=60, enabled=True):
        self.url = url
        self.name = name
        self.interval = interval
        self.enabled = enabled
        self.log = getLogger('tranny.rss.{0}'.format(name))
        self.log.info("Initialized RSS Feed")

    def update(self):
        t0 = time()
        delta = t0 - self.last_update
        if not delta > self.interval:
            return False
        self.last_update = t0
        self.parse()
        self.log.debug("Updated Feed")
        return True

    def parse(self):
        feed = parse(self.url)
        for entry in feed['entries']:
            release_name = entry['title']
            print(release_name)