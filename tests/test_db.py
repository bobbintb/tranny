from unittest import TestCase, main
from tranny import db


class DBTest(TestCase):
    def test_add(self):
        key = db.generate_release_key("Game.of.Kitties.S03E03.720p.HDTV.x264-EVOLVE")
        self.assertEqual("game.of.kitties-3_3", key)


if __name__ == '__main__':
    main()
