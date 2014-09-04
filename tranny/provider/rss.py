# -*- coding: utf-8 -*-
"""
RSS backend provider functionality
"""
from __future__ import unicode_literals
import feedparser
from tranny import app, provider, parser, datastore, release


class RSSFeed(provider.TorrentProvider):
    """
    Provides a RSS service to use as a backend retrieval source
    """
    def __init__(self, config_section):
        """
        :param config_section: Configuration section name
        :type config_section: string
        """
        super(RSSFeed, self).__init__(config_section)
        self.url = app.config.get(config_section, "url")
        self.interval = app.config.get_default(config_section, "interval", 60, int)
        self.enabled = app.config.getboolean(config_section, "enabled")
        app.logger.debug("Initialized RSS Provider ({} State): {}".format(
            'Enabled' if self.enabled else 'Disabled', self.name)
        )

    def fetch_releases(self):
        """
        Parse the feed yielding valid release data to be added to the torrent backend.

        This will attempt to fetch proper releases for existing releases if the fetch_proper config value
        is true.

        :return: a 3 element tuple containing (release_name, torrent_raw_data, section_name)
        :rtype: tranny.release.TorrentData
        """
        feed = feedparser.parse(self.url)
        return [self.parse_entry(f) for f in feed.get('entries', {})]

    def parse_entry(self, entry):
        """ Parse RSS entry data for qualified torrents to download

        :param entry: RSS Feed entry data
        :type entry: dict
        :return: A parsed release object ready to load into backend client or None on fail
        :rtype: release.TorrentData, None
        """
        try:
            release_name = entry.get('title', None)
            if not release_name:
                raise ValueError
        except (KeyError, ValueError):
            app.logger.warning("No title parsed from RSS feed. Malformed?")
            return None
        release_key = datastore.generate_release_key(release_name)
        if not release_key:
            return None

        section = parser.match_release(release_name)
        if section:
            if self.exists(release_key):
                if app.config.get_default("general", "fetch_proper", True, bool):
                    if not ".proper." in release_name.lower():
                        # Skip releases unless they are considered proper's
                        app.logger.debug(
                            "Skipped previously downloaded release ({0}): {1}".format(
                                release_key,
                                release_name
                            )
                        )
                        return None
            torrent_data = self._download_url(entry['link'])
            if not torrent_data:
                app.logger.error("Failed to download torrent data from server: {0}".format(entry['link']))
                return None
            data = release.TorrentData(str(release_name), torrent_data, section)
            return data
