# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from testcase import TrannyTestCase
from tranny import metadata, datastore


class MetaDataTest(TrannyTestCase):

    def test_update_trakt_tv(self):
        key = datastore.TVReleaseKey("The.Simpsons.S10E11.720p.HDTV.x264-GRP", "the.simpsons", 10, 11)
        metadata.update_trakt(key)


