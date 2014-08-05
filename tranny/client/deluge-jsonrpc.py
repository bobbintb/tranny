# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, absolute_import, with_statement
from tranny import client


class DelugeJSONRPCClient(client.ClientProvider):
    _config_key = "deluge-jsonrpc"

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
