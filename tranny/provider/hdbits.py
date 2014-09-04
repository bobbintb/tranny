# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, absolute_import
import requests
from tranny import provider, app
from tranny.exceptions import AuthenticationError, ApiError


class HDBits(provider.TorrentProvider):
    """
    .. _HDB API Docs: https://hdbits.org/wiki/index.php?title=API
    """
    def __init__(self, config_section):
        super(HDBits, self).__init__(config_section)
        self.endpoint = app.config.get_default(self._config_section, 'endpoint', 'https://hdbits.org/api')
        self.enabled = app.config.getboolean(self._config_section, 'enabled')
        self.interval = app.config.get_default(self._config_section, 'interval', self.interval, int)
        app.logger.info("Initialized HDBits Provider ({} State)".format(
            'Enabled' if self.enabled else 'Disabled')
        )

    def _request(self, method):
        pass

    def find_matches(self):
        return []
