# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, absolute_import, with_statement
from twisted.internet import reactor
from tranny import client


class DelugeClient(client.ClientProvider):
    _config_key = "transmission"

    def __init__(self, host=None, port=None, user=None, password=None):
        self._reactor = reactor.run()
        self.connected = False
        self._client = client.connect()
        self._client.addCallback(self.on_connect_success)

    def on_connect_success(self, result):
        self.connected = True

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
