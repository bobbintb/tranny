# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import os
from client_test_runner import TorrentTests
from tranny.app import config
from tranny.client.transmission import TransmissionClient

live_test = bool(int(os.environ.get('TEST_TRANSMISSION', '0')))


@unittest.skipUnless(live_test, "Not configured for live tests")
class TransmissionClientTest(TorrentTests):

    def make_client(self):
        return TransmissionClient(**config.get_section_values(TransmissionClient.config_key))


if __name__ == '__main__':
    unittest.main()
