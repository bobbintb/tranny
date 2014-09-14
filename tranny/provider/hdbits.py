# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, absolute_import
from tranny import provider
from tranny.app import config


class HDBits(provider.TorrentProvider):
    """
    .. _HDB API Docs: https://hdbits.org/wiki/index.php?title=API
    """
    def __init__(self, config_section):
        super(HDBits, self).__init__(config_section)
        self.endpoint = config.get_default(self._config_section, 'endpoint', 'https://hdbits.org/api')
        self.enabled = config.getboolean(self._config_section, 'enabled')
        self.interval = config.get_default(self._config_section, 'interval', self.interval, int)

    def _request(self, method):
        pass

    def find_matches(self):
        return []
