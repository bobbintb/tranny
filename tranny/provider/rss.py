# -*- coding: utf-8 -*-
"""
RSS backend provider functionality
"""

import feedparser
from tranny import app
from tranny import provider
from tranny import parser
from tranny import release
from tranny import net
from tranny.torrent import Torrent


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

    def fetch_releases(self, session):
        """
        Parse the feed yielding valid release data to be added to the torrent backend.

        This will attempt to fetch proper releases for existing releases if the fetch_proper config value
        is true.

        :param session: DB Session
        :type session: sqlalchemy.orm.session.Session
        :return: a 3 element tuple containing (release_name, torrent_raw_data, section_name)
        :rtype: tranny.release.TorrentData
        """
        for entry in feedparser.parse(self.url).get('entries', {}):
            torrent_data = self.parse_entry(session, entry)
            if torrent_data:
                yield torrent_data

    def parse_entry(self, session, entry):
        """ Parse RSS entry data for qualified torrents to download

        :param session: DB Session
        :type session: sqlalchemy.orm.session.Session
        :param entry: RSS Feed entry data
        :type entry: dict
        :return: A parsed release object ready to load into backend client or None on fail
        :rtype: release.TorrentData, None
        """

        release_name = entry.get('title', "")
        if not release_name:
            self.log.warning("No title parsed from RSS feed. Malformed?")
            return False
        release_info = parser.parse_release(release_name)
        if not release_info.release_key:
            self.log.warning("No release key parsed from release name: {}".format(release_name))
            return False
        release_key = release_info.release_key
        section_name = parser.validate_section(release_info)
        if not section_name or section_name == "section_movie":
            return False
        if self.exists(session, release_key) and not self.is_replacement(release_info):
            return False
        torrent_data = net.http_request(entry['link'], json=False)
        if not torrent_data:
            self.log.error("Failed to download torrent data from server: {0}".format(entry['link']))
            return False
        data = release.TorrentData(bytes(release_name), torrent_data, section_name), release_info
        torrent = Torrent.from_str(torrent_data)
        if not parser.valid_size(torrent, section_name):
            return False
        return data
