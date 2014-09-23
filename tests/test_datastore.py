# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from tranny import parser
from testcase import TrannyTestCase


class DataStoreTest(TrannyTestCase):
    def test_generate_release_key(self):
        args = [
            [u"f1-{}".format(datetime.now().isocalendar()[1]),
             u"F1.2012.Canadian.Grand.Prix.Qualifying.720p.HDTV.x264-XX", parser.TVSingleReleaseKey],
            [u"first.snow-2006", u'First Snow 2006 BRRip XvidHD 720p-XX', parser.MovieReleaseKey],
            [u"conan-2013_04_15", u"Conan.2013.4.15.Chelsea.Handler.HDTV.x264-XX", parser.TVDailyReleaseKey],
            [u"conan-2013_04_15", u"Conan.2013.04.15.Chelsea.Handler.HDTV.x264-XX", parser.TVDailyReleaseKey],
            [u"game.of.kitties-3_3", u"Game.of.Kitties.S03E03.720p.HDTV.x264-XX", parser.TVReleaseKey]

        ]
        for i in args:
            release = parser.parse_release(i[1])
            self.assertEqual(release.release_key, i[0])
            self.assertEqual(type(release.release_key), i[2])
