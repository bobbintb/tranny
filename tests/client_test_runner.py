# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import tempfile
import time
import unittest
import os
from testcase import TrannyTestCase, get_fixture, client_env
from tranny.client import TorrentState
from tranny.torrent import Torrent


class TorrentTests(TrannyTestCase):
    live_test = False

    test_file_1 = get_fixture('linux-iso.torrent')
    test_file_2 = get_fixture('linux-iso-2.torrent')
    test_file_3 = get_fixture('linux-iso-3.torrent')
    torrent = Torrent.from_file(test_file_1)
    torrent2 = Torrent.from_file(test_file_2)
    torrent3 = Torrent.from_file(test_file_3)

    def sleep_live(self, t):
        if self.live_test:
            time.sleep(t)

    def _wipe_all(self):
        try:
            for torrent in self.client.torrent_list():
                self.client.torrent_remove(torrent.info_hash, remove_data=True)
        except:
            pass

    def make_client(self):
        raise NotImplementedError("")

    def setUp(self):
        self.client = self.make_client()
        self.client_name = self.client.config_key.split("_")[1]
        self._wipe_all()

    def tearDown(self):
        self._wipe_all()
        time.sleep(1)

    def test_client_version(self):
        with client_env(self.track("torrent_version"), self.live_test):
            ver = self.client.client_version()
        num, rev = ver.split(" ")
        self.assertTrue(float(int(rev[1:][:-1])) > 2)
        self.assertTrue(rev > 10000)

    def test_torrent_add(self):
        with client_env(self.track("torrent_add_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_add_b"), self.live_test):
            torrent = self.client.torrent_status(self.torrent.info_hash)
            self.assertEqual(torrent.info_hash, self.torrent.info_hash)

    def test_current_speeds(self):
        with client_env(self.track("torrent_current_speeds"), self.live_test):
            speed = self.client.current_speeds()
        self.assertTrue(len(speed) == 2)
        self.assertGreaterEqual(speed[0], 0)
        self.assertGreaterEqual(speed[1], 0)

    def test_torrent_peers(self):
        with client_env(self.track("torrent_peers_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        self.sleep_live(10)
        with client_env(self.track("torrent_peers_b"), self.live_test):
            peers = self.client.torrent_peers(self.torrent.info_hash)
        self.assertTrue(len(peers) > 0)
        self.assertSetEqual({'client', 'down_speed', 'ip', 'progress', 'up_speed', 'country'}, set(peers[0].keys()))

    def test_torrent_files(self):
        with client_env(self.track("torrent_files_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_files_b"), self.live_test):
            files = self.client.torrent_files(self.torrent.info_hash)
        self.assertTrue(files)

    def test_torrent_speed(self):
        with client_env(self.track("torrent_speed_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_speed_b"), self.live_test):
            speed = self.client.torrent_speed(self.torrent.info_hash)
        self.assertTrue(speed)

    def test_torrent_status(self):
        with client_env(self.track("torrent_status_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        self.sleep_live(5)
        with client_env(self.track("torrent_status_b"), self.live_test):
            status = self.client.torrent_status(self.torrent.info_hash)
        self.assertTrue(status)

    def test_torrent_queue_up(self):
        with client_env(self.track("torrent_queue_up_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_up_b"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
        self.assertEqual(torrent_a.queue_position, 0)
        with client_env(self.track("torrent_queue_up_c"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_2, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_up_d"), self.live_test):
            torrent_b = self.client.torrent_status(self.torrent2.info_hash)
        self.assertEqual(torrent_b.queue_position, 1)

        with client_env(self.track("torrent_queue_up_e"), self.live_test):
            self.client.torrent_queue_up(self.torrent2.info_hash)
        with client_env(self.track("torrent_queue_up_f"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
        self.assertEqual(torrent_a.queue_position, 1)
        with client_env(self.track("torrent_queue_up_g"), self.live_test):
            torrent_b = self.client.torrent_status(self.torrent2.info_hash)
        self.assertEqual(torrent_b.queue_position, 0)

    def test_torrent_queue_down(self):
        with client_env(self.track("torrent_queue_down_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_down_b"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
        self.assertEqual(torrent_a.queue_position, 0)
        with client_env(self.track("torrent_queue_down_c"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_2, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_down_d"), self.live_test):
            torrent_b = self.client.torrent_status(self.torrent2.info_hash)
        self.assertEqual(torrent_b.queue_position, 1)
        with client_env(self.track("torrent_queue_down_e"), self.live_test):
            self.client.torrent_queue_down(self.torrent.info_hash)
        with client_env(self.track("torrent_queue_down_f"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
        self.assertEqual(torrent_a.queue_position, 1)

        with client_env(self.track("torrent_queue_down_g"), self.live_test):
            torrent_b = self.client.torrent_status(self.torrent2.info_hash)
        self.assertEqual(torrent_b.queue_position, 0)

    def test_torrent_queue_top(self):
        with client_env(self.track("torrent_queue_top_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_top_b"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
        self.assertEqual(torrent_a.queue_position, 0)
        with client_env(self.track("torrent_queue_top_c"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_2, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_top_d"), self.live_test):
            torrent_b = self.client.torrent_status(self.torrent2.info_hash)
        self.assertEqual(torrent_b.queue_position, 1)

        with client_env(self.track("torrent_queue_top_e"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_3, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_top_f"), self.live_test):
            torrent_c = self.client.torrent_status(self.torrent3.info_hash)
        self.assertEqual(torrent_c.queue_position, 2)

        with client_env(self.track("torrent_queue_top_g"), self.live_test):
            self.assertTrue(self.client.torrent_queue_top(self.torrent3.info_hash))

        with client_env(self.track("torrent_queue_top_h"), self.live_test):
            torrent_c = self.client.torrent_status(self.torrent3.info_hash)
            self.assertEqual(torrent_c.queue_position, 0)

        with client_env(self.track("torrent_queue_top_i"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
            self.assertEqual(torrent_a.queue_position, 1)

        with client_env(self.track("torrent_queue_top_j"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent2.info_hash)
            self.assertEqual(torrent_a.queue_position, 2)

    def test_torrent_queue_bottom(self):
        with client_env(self.track("torrent_queue_bottom_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_bottom_b"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
        self.assertEqual(torrent_a.queue_position, 0)
        with client_env(self.track("torrent_queue_bottom_c"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_2, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_bottom_d"), self.live_test):
            torrent_b = self.client.torrent_status(self.torrent2.info_hash)
        self.assertEqual(torrent_b.queue_position, 1)

        with client_env(self.track("torrent_queue_bottom_e"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_3, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_bottom_f"), self.live_test):
            torrent_c = self.client.torrent_status(self.torrent3.info_hash)
        self.assertEqual(torrent_c.queue_position, 2)

        with client_env(self.track("torrent_queue_bottom_g"), self.live_test):
            self.assertTrue(self.client.torrent_queue_bottom(self.torrent.info_hash))

        with client_env(self.track("torrent_queue_bottom_h"), self.live_test):
            torrent_c = self.client.torrent_status(self.torrent3.info_hash)
            self.assertEqual(torrent_c.queue_position, 1)

        with client_env(self.track("torrent_queue_bottom_i"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
            self.assertEqual(torrent_a.queue_position, 2)

        with client_env(self.track("torrent_queue_bottom_j"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent2.info_hash)
            self.assertEqual(torrent_a.queue_position, 0)

    def test_torrent_reannounce(self):
        with client_env(self.track("torrent_reannounce_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_reannounce_b"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
            self.assertEqual(torrent_a.next_announce, 0)
        time.sleep(5)
        with client_env(self.track("torrent_reannounce_c"), self.live_test):
            self.client.torrent_reannounce(self.torrent.info_hash)
        with client_env(self.track("torrent_reannounce_d"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
            self.assertGreater(torrent_a.next_announce, 0)

    def test_disconnect(self):
        self.assertTrue(self.client.disconnect())

    def test_torrent_recheck(self):
        # Not sure best way to check this..
        with client_env(self.track("torrent_recheck_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_recheck_b"), self.live_test):
            self.assertTrue(self.client.torrent_recheck(self.torrent.info_hash))

    @unittest.skip("Not sure how to test yet")
    def test_torrent_pause(self):
        with client_env(self.track("torrent_pause_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_pause_b"), self.live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
            self.assertIn(torrent_a.state, [TorrentState.PAUSED, TorrentState.CHECKING, TorrentState.DOWNLOADING])
        with client_env(self.track("torrent_pause_c"), self.live_test):
            self.assertTrue(self.client.torrent_pause(self.torrent.info_hash))

    def test_torrent_start(self):
        with client_env(self.track("torrent_start_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        time.sleep(2)
        with client_env(self.track("torrent_start_b"), self.live_test):
            self.assertTrue(self.client.torrent_pause(self.torrent.info_hash))
        time.sleep(2)
        with client_env(self.track("torrent_start_c"), self.live_test):
            status = self.client.torrent_status(self.torrent.info_hash)
            self.assertEqual(status.state, TorrentState.PAUSED)
        time.sleep(2)
        with client_env(self.track("torrent_start_d"), self.live_test):
            self.assertTrue(self.client.torrent_start(self.torrent.info_hash))
        time.sleep(2)
        with client_env(self.track("torrent_start_e"), self.live_test):
            status = self.client.torrent_status(self.torrent.info_hash)
            self.assertIn(status.state, [TorrentState.STARTED, TorrentState.DOWNLOADING])

    def test_torrent_add_duplicate(self):
        with client_env(self.track("torrent_add_duplicate_a"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))

        with client_env(self.track("torrent_add_duplicate_b"), self.live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
