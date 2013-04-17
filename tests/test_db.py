from unittest import TestCase, main
from tranny import db


class DBTest(TestCase):
    def test_add(self):
        args = [
            ["game.of.kitties-3_3", "Game.of.Kitties.S03E03.720p.HDTV.x264-EVOLVE"],
            ["first.snow", u'First Snow 2006 BRRip XvidHD 720p-NPW']
        ]
        for expected, release_name in args:
            self.assertEqual(expected, db.generate_release_key(release_name))


if __name__ == '__main__':
    main()
