# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals
import unittest
import os
from testcase import TrannyTestCase
from tranny.client import qbittorrent


class MockQBittorrentClient(object):
    def torrent_list(self):
        return


@unittest.skipUnless(os.environ.get('TEST_QBITTORRENT', False), "Not configured for live tests")
class QBTTest(TrannyTestCase):
    def test_torrent_list(self):
        torrent = {
            'hash': '9a8777601b7dbe0c2ee1b1e730bd64bbc7ef0e78',
            'name': 'Jimmy.Fallon.2014.08.20.Jared.Leto.720p.HDTV.x264-CROOKS',
            'ratio': '0.0',
            'priority': '*',
            'state': 'downloading',
            'eta': '1d 1h',
            'num_seeds': '16 (23)',
            'num_leechs': '0 (1)',
            'progress': 0.187561988830566,
            'size': '1.0 GiB',
            'dlspeed': '10.5 KiB/s',
            'upspeed': '0 B/s'
        }

        client = qbittorrent.QBittorrentClient(password='test')
        parsed_torrent = client.parse_torrent_info(torrent)
        self.assertEqual(
            parsed_torrent['info_hash'],
            '9a8777601b7dbe0c2ee1b1e730bd64bbc7ef0e78'
        )
