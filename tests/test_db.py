# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tranny import datastore
from testcase import TrannyTestCase


class DataStoreTest(TrannyTestCase):
    def test_generate_release_key(self):
        args = [
            [u"first.snow-2006", u'First Snow 2006 BRRip XvidHD 720p-XX', datastore.MovieReleaseKey],
            [u"conan-2013_04_15", u"Conan.2013.4.15.Chelsea.Handler.HDTV.x264-XX", datastore.TVDailyReleaseKey],
            [u"conan-2013_04_15", u"Conan.2013.04.15.Chelsea.Handler.HDTV.x264-XX", datastore.TVDailyReleaseKey],
            [u"game.of.kitties-3_3", u"Game.of.Kitties.S03E03.720p.HDTV.x264-XX", datastore.TVReleaseKey],
            #[u"f1-2012", u"F1.2012.Canadian.Grand.Prix.Qualifying.720p.HDTV.x264-XX", datastore.TVReleaseKey]
        ]
        for i in args:
            key = datastore.generate_release_key(i[1])
            self.assertEqual(key, i[0])
            self.assertEqual(type(key), i[2])
