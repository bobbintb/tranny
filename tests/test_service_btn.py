# -*- coding: utf-8 -*-

import unittest
from .testcase import TrannyTestCase, tapedeck
from tranny.app import config
from tranny.provider.broadcastthenet import BroadcastTheNet

btn_api = config.get_default("provider_broadcastthenet", "api_token", False)


@unittest.skipUnless(btn_api, "No API Key set for BTN")
class BTNAPITest(TrannyTestCase):
    def setUp(self):
        self.api = BroadcastTheNet()

    def test_user_info(self):
        response = self.api.user_info()
        self.assertTrue(response)

    def test_get_newest(self):
        response = self.api.get_torrents_browse(10)
        self.assertEqual(10, len(response['torrents']))

    def test_get_torrent_url(self):
        with tapedeck.use_cassette(self.track("test_get_torrent_url_a")):
            torrent_ids = list(self.api.get_torrents_browse(1)['torrents'].keys())
        for torrent_id in torrent_ids:
            with tapedeck.use_cassette(self.track("test_get_torrent_url_{}".format(torrent_id))):
                url = self.api.get_torrent_url(torrent_id)
            self.assertTrue(torrent_id in url)

    def test_find_matches(self):
        r = []
        for release in self.api.find_matches():
            r.append(release)
        self.assertEqual(10, len(r))


if __name__ == '__main__':
    unittest.main()
