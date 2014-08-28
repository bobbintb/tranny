# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, absolute_import
from tranny.client import qbittorrent
from testcase import TrannyTestCase

class QBTTest(TrannyTestCase):

    def test_torrent_list(self):
        client = qbittorrent.QBittorrentClient(password='test')
        torrents = client.torrent_list()
        self.assertTrue(torrents)
