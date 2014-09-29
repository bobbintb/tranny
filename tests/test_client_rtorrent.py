# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import os
from tests.testcase import TrannyTestCase


@unittest.skipUnless(os.environ.get('TEST_RTORRENT', False), "Not configured for live tests")
class RTorrentTest(TrannyTestCase):
    def test_load(self):
        pass
