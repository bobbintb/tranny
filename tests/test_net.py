# -*- coding: utf-8 -*-
from __future__ import unicode_literals, with_statement
import tempfile
from shutil import rmtree
from os.path import exists, join
from os import remove
from testcase import tapedeck, TrannyTestCase
from unittest import main
from tranny import net


class NetTest(TrannyTestCase):
    tmp_dir = None

    def setUp(self):
        self.url_ok = "http://mirror.centos.org/centos/timestamp.txt"

    def tearDown(self):
        if exists("test_name.torrent"):
            remove("test_name.torrent")
        if self.tmp_dir and exists(self.tmp_dir):
            rmtree(self.tmp_dir)
        self.tmp_dir = None

    def test_http_request_post(self):
        with tapedeck.use_cassette(self.track("test_http_request_post")):
            resp = net.http_request('https://posttestserver.com/post.php', data={'test': 1}, method='post')
        self.assertTrue("dumped 1" in resp.content)

    def test_download_ok(self):
        self.tmp_dir = tempfile.mkdtemp()
        with tapedeck.use_cassette(self.track("test_download_ok")):
            self.assertTrue(net.download("test_name", self.url_ok, self.tmp_dir, extension=".test"))
        with open(join(self.tmp_dir, "test_name.test")) as tf:
            self.assertTrue(len(tf.read()))

    def test_download_fail(self):
        with tapedeck.use_cassette(self.track("test_download_fail")):
            status = net.download("bs_name", "http://bs.url.com/blah.torrent")
        self.assertFalse(status)

    def test_parse_net_speed_value(self):
        self.assertEqual(10752.0, net.parse_net_speed_value(u'10.5 KiB/s'))
        self.assertEqual(11010048.0, net.parse_net_speed_value(u'10.5 MiB/s'))
        self.assertEqual(10500000.0, net.parse_net_speed_value(u'10.5 mb/s'))

    def test_ip2int(self):
        self.assertEqual(1010580540, net.ip2int("60.60.60.60"))

    def test_int2ip(self):
        self.assertEqual("60.60.60.60", net.int2ip(1010580540))

if __name__ == '__main__':
    main()

