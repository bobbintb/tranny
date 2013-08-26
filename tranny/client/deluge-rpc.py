# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, absolute_import, with_statement
from base64 import b64encode
from ..app import config, logger
from ..client import ClientProvider


class DelugeRPCClient(ClientProvider):
    _config_key = "transmission"

    def __init__(self, host=None, port=None, user=None, password=None):
        pass

    def client_version(self):
        return "Transmission XX"

    def add(self, data, download_dir=None):
        pass

    def list(self):
        """ Get a list of currently loaded torrents from the client

        :return:
        :rtype:
        """
        return []
