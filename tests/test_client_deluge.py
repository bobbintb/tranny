# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import os
from tests.client_test_runner import TorrentTests
from tranny.app import config
from tranny.client.deluge import DelugeClient


class DelugeClientTests(TorrentTests):

    live_test = bool(int(os.environ.get('TEST_DELUGE', '0')))

    def make_client(self):
        client = DelugeClient(**config.get_section_values(DelugeClient.config_key))
        client.authenticate()
        return client

if __name__ == '__main__':
    unittest.main()
