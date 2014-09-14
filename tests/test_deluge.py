# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals

from testcase import TrannyTestCase
from tranny.app import config
from tranny.client.deluge import DelugeClient
from tranny.release import TorrentData


class DelugeTest(TrannyTestCase):
    def setUp(self):
        self.load_config(self.get_fixture("test_config.ini"))
        self.client = DelugeClient()

    def test_upload(self):
        torrent = TorrentData(
            'Jimmy.Fallon.2014.01.01.John.Smith.HDTV.x264-GROUP',
            open(self.get_fixture('CentOS-6.3-x86_64-bin-DVD1to2.torrent'), 'rb').read(),
            'section_tv')
        self.assertTrue(self.client.add(torrent, config.get(torrent.section, 'dl_path')))


