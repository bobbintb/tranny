# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase, main
from tranny import datastore


class DBTest(TestCase):
    def test_add(self):
        args = [
            ["F1.2012.Canadian.Grand.Prix.Qualifying", "F1.2012.Canadian.Grand.Prix.Qualifying.720p.HDTV.x264-XX"],
            ["first.snow-2006", 'First Snow 2006 BRRip XvidHD 720p-XX'],
            ["conan-2013_04_15", "Conan.2013.4.15.Chelsea.Handler.HDTV.x264-XX"],
            ["conan-2013_04_15", "Conan.2013.04.15.Chelsea.Handler.HDTV.x264-XX"],
            ["game.of.kitties-3_3", "Game.of.Kitties.S03E03.720p.HDTV.x264-XX"]
        ]
        for expected, release_name in args:
            self.assertEqual(expected, datastore.generate_release_key(release_name))


if __name__ == '__main__':
    main()
