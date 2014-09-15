from unittest import TestCase, main
from os.path import join, dirname
from requests.exceptions import ConnectionError
from tranny.client.utorrent import UTorrentClient
from testcase import TrannyTestCase


class UTorrentClientTest(TrannyTestCase):
    def setUp(self):
        self.test_file_1 = join(dirname(__file__), 'test_data', 'CentOS-6.3-x86_64-bin-DVD1to2.torrent')
        try:
            self.client = UTorrentClient()
        except ConnectionError:
            self.skipTest("uTorrent not available")

    def test_token(self):
        token = self.client.token
        self.assertEqual(64, len(token))

    def test_get_version(self):
        version = self.client.get_version()
        self.assertTrue(version)

    def test_get_settings(self):
        settings = self.client.get_settings()
        self.assertTrue(settings)

    def test_add(self):
        torrent_data = open(self.test_file_1, "rb").read()
        self.assertTrue(self.client.add(torrent_data))


if __name__ == '__main__':
    main()
