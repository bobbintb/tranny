# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import tempfile
import time
import unittest
import os
from testcase import TrannyTestCase, get_fixture, client_env
from tranny.app import config
from tranny.client import TorrentState
from tranny.torrent import Torrent
from tranny.client.transmission import TransmissionClient

live_test = bool(int(os.environ.get('TEST_TRANSMISSION', '0')))


def sleep_live(t):
    if live_test:
        time.sleep(t)


#@unittest.skipUnless(live_test, "Not configured for live tests")
class TransmissionClientTest(TrannyTestCase):

    test_file_1 = get_fixture('linux-iso.torrent')
    test_file_2 = get_fixture('linux-iso-2.torrent')
    test_file_3 = get_fixture('linux-iso-3.torrent')

    def setUp(self):
        self.client = TransmissionClient(**config.get_section_values(TransmissionClient.config_key))
        self.torrent = Torrent.from_file(self.test_file_1)
        self.torrent2 = Torrent.from_file(self.test_file_2)
        self.torrent3 = Torrent.from_file(self.test_file_3)
        self._wipe_all()

    def _wipe_all(self):
        try:
            for torrent in self.client.torrent_list():
                self.client.torrent_remove(torrent.info_hash, remove_data=True)
        except:
            pass

    def tearDown(self):
        self._wipe_all()
        time.sleep(1)

    def test_client_version(self):
        with client_env(self.track("torrent_version"), live_test):
            ver = self.client.client_version()
        num, rev = ver.split(" ")
        self.assertTrue(float(int(rev[1:][:-1])) > 2)
        self.assertTrue(rev > 10000)

    def test_torrent_add(self):
        with client_env(self.track("torrent_add_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_add_b"), live_test):
            torrent = self.client.torrent_status(self.torrent.info_hash)
            self.assertEqual(torrent.info_hash, self.torrent.info_hash)

    def test_current_speeds(self):
        with client_env(self.track("torrent_current_speeds"), live_test):
            speed = self.client.current_speeds()
        self.assertTrue(len(speed) == 2)
        self.assertGreaterEqual(speed[0], 0)
        self.assertGreaterEqual(speed[1], 0)

    def test_torrent_peers(self):
        with client_env(self.track("torrent_peers_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        sleep_live(10)
        with client_env(self.track("torrent_peers_b"), live_test):
            peers = self.client.torrent_peers(self.torrent.info_hash)
        self.assertTrue(len(peers) > 0)
        self.assertSetEqual({'client', 'down_speed', 'ip', 'progress', 'up_speed', 'country'}, set(peers[0].keys()))

    def test_torrent_files(self):
        with client_env(self.track("torrent_files_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_files_b"), live_test):
            files = self.client.torrent_files(self.torrent.info_hash)
        self.assertTrue(files)

    def test_torrent_speed(self):
        with client_env(self.track("torrent_speed_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_speed_b"), live_test):
            speed = self.client.torrent_speed(self.torrent.info_hash)
        self.assertTrue(speed)

    def test_torrent_status(self):
        with client_env(self.track("torrent_status_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        sleep_live(5)
        with client_env(self.track("torrent_status_b"), live_test):
            status = self.client.torrent_status(self.torrent.info_hash)
        self.assertTrue(status)

    def test_torrent_queue_up(self):
        with client_env(self.track("torrent_queue_up_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_up_b"), live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
        self.assertEqual(torrent_a.queue_position, 0)
        with client_env(self.track("torrent_queue_up_c"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_2, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_up_d"), live_test):
            torrent_b = self.client.torrent_status(self.torrent2.info_hash)
        self.assertEqual(torrent_b.queue_position, 1)

        with client_env(self.track("torrent_queue_up_e"), live_test):
            self.client.torrent_queue_up(self.torrent2.info_hash)
        with client_env(self.track("torrent_queue_up_f"), live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
        self.assertEqual(torrent_a.queue_position, 1)
        with client_env(self.track("torrent_queue_up_g"), live_test):
            torrent_b = self.client.torrent_status(self.torrent2.info_hash)
        self.assertEqual(torrent_b.queue_position, 0)

    def test_torrent_queue_down(self):
        with client_env(self.track("torrent_queue_down_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_down_b"), live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
        self.assertEqual(torrent_a.queue_position, 0)
        with client_env(self.track("torrent_queue_down_c"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_2, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_down_d"), live_test):
            torrent_b = self.client.torrent_status(self.torrent2.info_hash)
        self.assertEqual(torrent_b.queue_position, 1)
        with client_env(self.track("torrent_queue_down_e"), live_test):
            self.client.torrent_queue_down(self.torrent.info_hash)
        with client_env(self.track("torrent_queue_down_f"), live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
        self.assertEqual(torrent_a.queue_position, 1)

        with client_env(self.track("torrent_queue_down_g"), live_test):
            torrent_b = self.client.torrent_status(self.torrent2.info_hash)
        self.assertEqual(torrent_b.queue_position, 0)

    def test_torrent_queue_top(self):
        with client_env(self.track("torrent_queue_top_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_top_b"), live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
        self.assertEqual(torrent_a.queue_position, 0)
        with client_env(self.track("torrent_queue_top_c"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_2, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_top_d"), live_test):
            torrent_b = self.client.torrent_status(self.torrent2.info_hash)
        self.assertEqual(torrent_b.queue_position, 1)

        with client_env(self.track("torrent_queue_top_e"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_3, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_top_f"), live_test):
            torrent_c = self.client.torrent_status(self.torrent3.info_hash)
        self.assertEqual(torrent_c.queue_position, 2)

        with client_env(self.track("torrent_queue_top_g"), live_test):
            self.assertTrue(self.client.torrent_queue_top(self.torrent3.info_hash))

        with client_env(self.track("torrent_queue_top_h"), live_test):
            torrent_c = self.client.torrent_status(self.torrent3.info_hash)
            self.assertEqual(torrent_c.queue_position, 0)

        with client_env(self.track("torrent_queue_top_i"), live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
            self.assertEqual(torrent_a.queue_position, 1)

        with client_env(self.track("torrent_queue_top_j"), live_test):
            torrent_a = self.client.torrent_status(self.torrent2.info_hash)
            self.assertEqual(torrent_a.queue_position, 2)

    def test_torrent_queue_bottom(self):
        with client_env(self.track("torrent_queue_bottom_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_bottom_b"), live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
        self.assertEqual(torrent_a.queue_position, 0)
        with client_env(self.track("torrent_queue_bottom_c"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_2, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_bottom_d"), live_test):
            torrent_b = self.client.torrent_status(self.torrent2.info_hash)
        self.assertEqual(torrent_b.queue_position, 1)

        with client_env(self.track("torrent_queue_bottom_e"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_3, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_queue_bottom_f"), live_test):
            torrent_c = self.client.torrent_status(self.torrent3.info_hash)
        self.assertEqual(torrent_c.queue_position, 2)

        with client_env(self.track("torrent_queue_bottom_g"), live_test):
            self.assertTrue(self.client.torrent_queue_bottom(self.torrent.info_hash))

        with client_env(self.track("torrent_queue_bottom_h"), live_test):
            torrent_c = self.client.torrent_status(self.torrent3.info_hash)
            self.assertEqual(torrent_c.queue_position, 1)

        with client_env(self.track("torrent_queue_bottom_i"), live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
            self.assertEqual(torrent_a.queue_position, 2)

        with client_env(self.track("torrent_queue_bottom_j"), live_test):
            torrent_a = self.client.torrent_status(self.torrent2.info_hash)
            self.assertEqual(torrent_a.queue_position, 0)

    def test_torrent_reannounce(self):
        with client_env(self.track("torrent_reannounce_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_reannounce_b"), live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
            self.assertEqual(torrent_a.next_announce, 0)
        time.sleep(5)
        with client_env(self.track("torrent_reannounce_c"), live_test):
            self.client.torrent_reannounce(self.torrent.info_hash)
        with client_env(self.track("torrent_reannounce_d"), live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
            self.assertGreater(torrent_a.next_announce, 0)

    def test_disconnect(self):
        self.assertTrue(self.client.disconnect())

    def test_torrent_recheck(self):
        # Not sure best way to check this..
        with client_env(self.track("torrent_recheck_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_recheck_b"), live_test):
            self.assertTrue(self.client.torrent_recheck(self.torrent.info_hash))

    @unittest.skip("Not sure how to test yet")
    def test_torrent_pause(self):
        with client_env(self.track("torrent_pause_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        with client_env(self.track("torrent_pause_b"), live_test):
            torrent_a = self.client.torrent_status(self.torrent.info_hash)
            self.assertIn(torrent_a.state, [TorrentState.PAUSED, TorrentState.CHECKING, TorrentState.DOWNLOADING])
        with client_env(self.track("torrent_pause_c"), live_test):
            self.assertTrue(self.client.torrent_pause(self.torrent.info_hash))

    def test_torrent_start(self):
        with client_env(self.track("torrent_start_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))
        time.sleep(2)
        with client_env(self.track("torrent_start_b"), live_test):
            self.assertTrue(self.client.torrent_pause(self.torrent.info_hash))
        time.sleep(2)
        with client_env(self.track("torrent_start_c"), live_test):
            status = self.client.torrent_status(self.torrent.info_hash)
            self.assertEqual(status.state, TorrentState.PAUSED)
        time.sleep(2)
        with client_env(self.track("torrent_start_d"), live_test):
            self.assertTrue(self.client.torrent_start(self.torrent.info_hash))
        time.sleep(2)
        with client_env(self.track("torrent_start_e"), live_test):
            status = self.client.torrent_status(self.torrent.info_hash)
            self.assertIn(status.state, [TorrentState.STARTED, TorrentState.DOWNLOADING])

    def test_torrent_add_duplicate(self):
        with client_env(self.track("torrent_add_duplicate_a"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))

        with client_env(self.track("torrent_add_duplicate_b"), live_test):
            self.assertTrue(self.client.torrent_add(open(self.test_file_1, "rb").read(), tempfile.gettempdir()))

if __name__ == '__main__':
    unittest.main()
