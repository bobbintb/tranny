# -*- coding: utf-8 -*-

import unittest
import os
from tests.testcase import TrannyTestCase


@unittest.skipUnless(os.environ.get('TEST_RTORRENT', False), "Not configured for live tests")
class RTorrentTest(TrannyTestCase):
    def test_load(self):
        pass
