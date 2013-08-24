from logging import getLogger
from time import time
from ..models import DownloadEntity
from ..net import fetch_url


class TorrentProvider(object):
    def __init__(self, config, config_section):
        """ Provides a basic interface to generate new torrents from external services.

        :param config:
        :type config: tranny.configuration.Configuration
        :param config_section:
        :type config_section:
        :return:
        :rtype:
        """

        # Timestamp of last successful update
        self.last_update = 0
        self._config_section = config_section
        self.log = getLogger(self.name)
        self.config = config
        self.interval = self.config.get_default(config_section, "interval", 60, int)
        from tranny import session
        self.session = session

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
        if not delta > self.interval:
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
        torrent_data = fetch_url(url)
        return torrent_data

    def fetch_releases(self):
        raise NotImplementedError("Must override this method")

    def exists(self, release_key):
        try:
            e = self.session.query(DownloadEntity).filter_by(release_key=release_key).all()
        except Exception as err:
            self.log.exception(err)
            return False
        return e
