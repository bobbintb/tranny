from time import time
from logging import getLogger
from feedparser import parse as parse
from tranny.parser import match_release

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

    def find_matches(self):
        t0 = time()
        delta = t0 - self.last_update
        if not delta > self.interval:
            return []
        self.last_update = t0
        return self.parse()

    def parse(self):
        feed = parse(self.url)
        for entry in feed['entries']:
            release_name = entry['title']
            if match_release(release_name):
                yield release_name
