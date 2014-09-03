# -*- coding: utf-8 -*-
"""
Base implementation of a torrent provider. New providers should mostly be ok
just overriding the fetch_releases method.
"""
from __future__ import unicode_literals
from time import time
from tranny.app import config, logger
from tranny import models, net
from tranny.extensions import db


class TorrentProvider(object):
    """
    Base torrent provider used to download new releases from trackers
    """
    def __init__(self, config_section):
        """ Provides a basic interface to generate new torrents from external services.

        :param config:
        :type config: tranny.configuration.Configuration
        :param config_section:
        :type config_section:
        :return:
        :rtype:
        """

        # Timestamp of last successful update
        self.enabled = False
        self.last_update = 0
        self._config_section = config_section
        self.interval = config.get_default(config_section, "interval", 60, int)

    @property
    def name(self):
        return self._config_section.split("_")[1]

    def find_matches(self):
        """

        :return:
        :rtype:
        """
        t0 = time()
        delta = t0 - self.last_update
        if not delta > self.interval or not self.enabled:
            return []
        self.last_update = t0
        return self.fetch_releases()

    def _download_url(self, url):
        """ Fetch a torrent from the url provided

        :param url:
        :type url:
        :return:
        :rtype:
        """
        torrent_data = net.fetch_url(url)
        return torrent_data

    def fetch_releases(self):
        raise NotImplementedError("Must override this method")

    def exists(self, release_key):
        try:
            e = db.session.query(models.DownloadEntity).filter_by(release_key=release_key).all()
        except Exception as err:
            logger.exception(err)
            return False
        return e
