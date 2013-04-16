from time import time
from logging import getLogger
from feedparser import parse as parse
from tranny.parser import match_release
from tranny.net import download, fetch_url


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
            section = match_release(release_name)
            if section:
                torrent_data = self.download(entry['link'])
                if not torrent_data:
                    self.log.error("Failed to download torrent data from server: {0}".format(entry['link']))
                    continue

                yield str(release_name), torrent_data, section

    def download(self, url):
        torrent_data = fetch_url(url)
        return torrent_data
