import unittest
from tests import TrannyTestCase, get_fixture
from tranny.service.broadcastthenet import BroadcastTheNet
from tranny import init_config

try:
    btn_api = init_config(get_fixture("test_config.ini")).get("service_broadcastthenet", "api_token")
except:
    btn_api = False


@unittest.skipUnless(btn_api, "No API Key set for BTN")
class BTNAPITest(TrannyTestCase):
    def setUp(self):
        self.api = BroadcastTheNet(init_config(get_fixture("test_config.ini")))

    def test_user_info(self):
        response = self.api.user_info()
        self.assertTrue(response)

    def test_get_newest(self):
        response = self.api.get_torrents_browse(10)
        self.assertEqual(10, len(response['torrents']))

    def test_get_torrent_url(self):
        for torrent_id in self.api.get_torrents_browse(1)['torrents'].keys():
            url = self.api.get_torrent_url(torrent_id)
            self.assertTrue(torrent_id in url)

    def test_find_matches(self):
        r = []
        for release in self.api.find_matches():
            r.append(release)
        self.assertEqual(10, len(r))


if __name__ == '__main__':
    unittest.main()
