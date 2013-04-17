from time import time
from logging import getLogger
from feedparser import parse as parse
from tranny.parser import match_release
from tranny.net import fetch_url
from tranny.db import generate_release_key
from tranny.release import TorrentData


class RSSFeed(object):
    # Timestamp of last successful update
    last_update = 0

    def __init__(self, url, name="Unknown", interval=60, enabled=True):
        self.url = url
        self.name = name
        self.interval = interval
        self.enabled = enabled
        self.log = getLogger('tranny.rss.{0}'.format(name))
        self.log.info("Initialized RSS Feed: {0}".format(name))
        from tranny import config, datastore

        self.config = config
        self.datastore = datastore

    def find_matches(self):
        """

        :return:
        :rtype:
        """
        t0 = time()
        delta = t0 - self.last_update
        if not delta > self.interval:
            return []
        self.last_update = t0
        return self.parse()

    def parse(self):
        """
        Parse the feed yielding valid release data to be added to the torrent backend.

        This will attempt to fetch proper releases for existing releases if the fetch_proper config value
        is true.
        :return: a 3 element tuple containing (release_name, torrent_raw_data, section_name)
        :rtype: tranny.release.TorrentData
        """
        feed = parse(self.url)
        for entry in feed['entries']:
            try:
                release_name = entry['title']
                release_key = generate_release_key(release_name)
                if not release_key:
                    continue
                if release_key in self.datastore:
                    if self.config.get_default("general", "fetch_proper", True, bool):
                        if not ".proper." in release_name.lower():
                            # Skip releases unless they are considered proper's
                            self.log.debug(
                                "Skipped previously downloaded release ({0}): {1}".format(
                                    release_key,
                                    release_name

                                )
                            )
                            continue

                section = match_release(release_name)
                if section:
                    torrent_data = self.download(entry['link'])
                    if not torrent_data:
                        self.log.error("Failed to download torrent data from server: {0}".format(entry['link']))
                        continue

                    yield TorrentData(str(release_name), torrent_data, section)
            except Exception as err:
                self.log.error(err)

    def download(self, url):
        torrent_data = fetch_url(url)
        return torrent_data
