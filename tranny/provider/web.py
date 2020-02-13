# -*- coding: utf-8 -*-
"""
Dummy web provider class
"""

from tranny import provider


class WebProvider(provider.TorrentProvider):
    """
    This is a dummy class used to track web based uploads
    """
    def __init__(self, config_section=None):
        super(WebProvider, self).__init__("provider_web")
