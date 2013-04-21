from unittest import TestCase, main
from os.path import join, dirname
from tranny import init_config
from tranny.rpc.utorrent import UTorrentClient
from tests import get_fixture

config = init_config(get_fixture("test_config.ini"))


class UTorrentClientTest(TestCase):
    def setUp(self):
        self.test_file_1 = join(dirname(__file__), 'test_data', 'CentOS-6.3-x86_64-bin-DVD1to2.torrent')
        self.client = UTorrentClient(config)

    def test_token(self):
        token = self.client.token
        self.assertEqual(64, len(token))

    def test_get_version(self):
        version = self.client.get_version()
        self.assertTrue(version)


if __name__ == '__main__':
    main()
