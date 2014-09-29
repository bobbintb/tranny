# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import tempfile
import time
import unittest
from testcase import TrannyTestCase, get_fixture, tapedeck, client_env
from tranny import client
from tranny.app import config
from tranny.torrent import Torrent

live_test = bool(int(os.environ.get('TEST_TRANSMISSION', '0')))
#live_test = False

#@unittest.skipUnless(live_test, "Not configured for live tests")
class TransmissionClientTest(TrannyTestCase):
    def setUp(self):
        self.test_file_1 = get_fixture('linux-iso.torrent')
        config.set("general", "client", "transmission")
        self.client = client.init_client()
        self.torrent = Torrent.from_file(self.test_file_1)
        self._wipe_all()

    def _wipe_all(self):
        for torrent in self.client.torrent_list():
            self.client.torrent_remove(torrent.info_hash, remove_data=True)

    def tearDown(self):
        self._wipe_all()
        time.sleep(1)

    def test_client_version(self):
        ver = self.client.client_version()
        num, rev = ver.split(" ")
        self.assertTrue(float(int(rev[1:][:-1])) > 2)
        self.assertTrue(rev > 10000)

    def test_torrent_add(self):
        self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        self.assertIn(self.torrent.info_hash, [t.info_hash for t in self.client.torrent_list()])

    def test_current_speeds(self):
        speed = self.client.current_speeds()
        self.assertTrue(speed)

    def test_torrent_peers(self):
        with client_env(self.track("torrent_peers_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        if live_test:
            # wait for some peers to connect when live
            time.sleep(10)
        with client_env(self.track("torrent_peers_b"), live_test):
            peers = self.client.torrent_peers(self.torrent.info_hash)
        self.assertTrue(len(peers) > 0)
        self.assertSetEqual({'client', 'down_speed', 'ip', 'progress', 'up_speed'}, set(peers[0].keys()))

    def test_torrent_files(self):
        with client_env(self.track("torrent_files_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        files = self.client.torrent_files(self.torrent.info_hash)
        self.assertTrue(files)

    def test_torrent_speed(self):
        with client_env(self.track("torrent_speed_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_speed_b"), live_test):
            speed = self.client.torrent_speed(self.torrent.info_hash)
        self.assertTrue(speed)


if __name__ == '__main__':
    unittest.main()
