from logging import getLogger
from feedparser import parse as parse
from .provider import TorrentProvider
from .parser import match_release
from .db import generate_release_key
from .release import TorrentData


class RSSFeed(TorrentProvider):
    def __init__(self, config, config_section):
        super(RSSFeed, self).__init__(config, config_section)
        self.url = self.config.get(config_section, "url")
        self.interval = self.config.get_default(config_section, "interval", 60, int)
        self.enabled = self.config.getboolean(config_section, "enabled")
        self.log = getLogger('rss.{0}'.format(self.name))
        self.log.info("Initialized RSS Feed: {0}".format(self.name))

    def fetch_releases(self):
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
                    torrent_data = self._download_url(entry['link'])
                    if not torrent_data:
                        self.log.error("Failed to download torrent data from server: {0}".format(entry['link']))
                        continue
                    yield TorrentData(str(release_name), torrent_data, section)
            except Exception as err:
                self.log.error(err)


