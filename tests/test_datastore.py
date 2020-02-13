# -*- coding: utf-8 -*-

from datetime import datetime
from tranny import parser
from .testcase import TrannyTestCase


class DataStoreTest(TrannyTestCase):
    def test_generate_release_key(self):
        args = [
            ["f1-{}".format(datetime.now().isocalendar()[1]),
             "F1.2012.Canadian.Grand.Prix.Qualifying.720p.HDTV.x264-XX", parser.TVSingleReleaseKey],
            ["first.snow-2006", 'First Snow 2006 BRRip XvidHD 720p-XX', parser.MovieReleaseKey],
            ["conan-2013_04_15", "Conan.2013.4.15.Chelsea.Handler.HDTV.x264-XX", parser.TVDailyReleaseKey],
            ["conan-2013_04_15", "Conan.2013.04.15.Chelsea.Handler.HDTV.x264-XX", parser.TVDailyReleaseKey],
            ["game.of.kitties-3_3", "Game.of.Kitties.S03E03.720p.HDTV.x264-XX", parser.TVReleaseKey]

        ]
        for i in args:
            release = parser.parse_release(i[1])
            self.assertEqual(release.release_key, i[0])
            self.assertEqual(type(release.release_key), i[2])
