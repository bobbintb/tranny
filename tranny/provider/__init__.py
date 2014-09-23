# -*- coding: utf-8 -*-
"""
Base implementation of a torrent provider. New providers should mostly be ok
just overriding the fetch_releases method.
"""
from __future__ import unicode_literals
import logging
from time import time
from tranny.app import config, Session
from tranny.models import Download


class TorrentProvider(object):
    """
    Base torrent provider used to download new releases from trackers
    """
    def __init__(self, config_section):
        """ Provides a basic interface to generate new torrents from external services.

        :param config_section:
        :type config_section:
        """

        # Timestamp of last successful update
        self.enabled = False
        self.last_update = 0
        self._config_section = config_section
        self.interval = config.get_default(config_section, "interval", 60, int)
        self.log = logging.getLogger(config_section)
        self.log.debug("Initialized {} Provider ({} State): {}".format(
            self.__class__.__name__,
            'Enabled' if self.enabled else 'Disabled', self.name)
        )

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
            raise StopIteration
        self.last_update = t0
        session = Session()
        for torrent, release_info in self.fetch_releases(session):
            yield session, [torrent, release_info]

    def fetch_releases(self, session):
        """

        :param session:
        :type session: sqlalchemy.orm.session.Session
        """
        raise NotImplementedError("Must override this method")

    def exists(self, session, release_key):
        try:
            return session.query(Download).filter_by(release_key="{}".format(release_key)).all()
        except Exception as err:
            self.log.exception(err)
            return False

    def is_replacement(self, release_info):
        """

        :param release_info:
        """
        fetch_proper = config.get_default("general", "fetch_proper", True, bool)
        # Skip releases unless they are considered propers or repacks
        if fetch_proper and not (release_info.is_repack or release_info.is_repack):
            self.log.debug("Skipped previously downloaded release ({0}): {1}".format(
                release_info.release_key, release_info.release_name))
            return False
        return True
