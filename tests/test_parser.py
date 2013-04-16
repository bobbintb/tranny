from unittest import TestCase, main
from tranny import parser


class ReleaseTest(TestCase):
    release_a = 'The.Mentalist.S05E10.720p.HDTV.X264-DIMENSION'
    release_b = 'Homeland.S02E11.HDTV.x264-EVOLVE'
    release_c = 'Falcon.1x04.The.Silent.And.The.Damned.Part.Two.HDTV.x264-FoV'
    release_d = "Easy.Money.2010.LIMITED.DVDRip.XviD-VH-PROD"

    def test_parse_season(self):
        self.assertTupleEqual((5, 10), parser.parse_season(self.release_a))
        self.assertTupleEqual((2, 11), parser.parse_season(self.release_b))
        self.assertTupleEqual((1, 4), parser.parse_season(self.release_c))

    def test_parse_release(self):
        self.assertEqual("The.Mentalist", parser.parse_release(self.release_a))
        self.assertEqual("Homeland", parser.parse_release(self.release_b))
        self.assertEqual("Falcon", parser.parse_release(self.release_c))
        self.assertEqual("Easy.Money", parser.parse_release(self.release_d))

    def test_match_release(self):
        self.assertTrue(parser.match_release(self.release_a))
        self.assertTrue(parser.match_release(self.release_b))
        self.assertFalse(parser.match_release(self.release_c))


if __name__ == '__main__':
    main()
