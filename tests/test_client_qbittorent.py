# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, absolute_import
from tranny.client import qbittorrent
from testcase import TrannyTestCase


class MockQBittorrentClient(object):
    def torrent_list(self):
        return


class QBTTest(TrannyTestCase):
    def test_torrent_list(self):
        torrents = [
            {
                u'hash': u'9a8777601b7dbe0c2ee1b1e730bd64bbc7ef0e78',
                u'name': u'Jimmy.Fallon.2014.08.20.Jared.Leto.720p.HDTV.x264-CROOKS',
                u'ratio': u'0.0',
                u'priority': u'*',
                u'state': u'downloading',
                u'eta': u'1d 1h',
                u'num_seeds': u'16 (23)',
                u'num_leechs': u'0 (1)',
                u'progress': 0.187561988830566,
                u'size': u'1.0 GiB',
                u'dlspeed': u'10.5 KiB/s',
                u'upspeed': u'0 B/s'
            }
        ]

        client = qbittorrent.QBittorrentClient(password='test')
        torrents = client._parse_torrent_list(torrents)
        self.assertTrue(torrents)
