from os.path import exists
from os import remove
from unittest import TestCase, main
from tranny import net


class NetTest(TestCase):
    def setUp(self):
        self.url_ok = "http://mirror.centos.org/centos/6.3/isos/x86_64/CentOS-6.3-x86_64-bin-DVD1to2.torrent"

    def tearDown(self):
        if exists("test_name.torrent"):
            remove("test_name.torrent")

    def test_download_ok(self):
        status = net.download("test_name", self.url_ok, "./")
        self.assertTrue(status)

    def test_download_fail(self):
        status = net.download("bs_name", "http://bs.url.com/blah.torrent", "./")
        self.assertFalse(status)

    def test_parse_net_speed_value(self):
        self.assertEqual(10752.0, net.parse_net_speed_value(u'10.5 KiB/s'))
        self.assertEqual(11010048.0, net.parse_net_speed_value(u'10.5 MiB/s'))
        self.assertEqual(10500000.0, net.parse_net_speed_value(u'10.5 mb/s'))

if __name__ == '__main__':
    main()

