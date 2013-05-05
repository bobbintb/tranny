from unittest import TestCase, main
from tranny import datastore


class DBTest(TestCase):
    def test_add(self):
        args = [
            ["conan-2013_04_15", "Conan.2013.4.15.Chelsea.Handler.HDTV.x264-2HD"],
            ["conan-2013_04_15", "Conan.2013.04.15.Chelsea.Handler.HDTV.x264-2HD"],
            ["game.of.kitties-3_3", "Game.of.Kitties.S03E03.720p.HDTV.x264-EVOLVE"],
            ["first.snow", u'First Snow 2006 BRRip XvidHD 720p-NPW'],
        ]
        for expected, release_name in args:
            self.assertEqual(expected, datastore.generate_release_key(release_name))


if __name__ == '__main__':
    main()
