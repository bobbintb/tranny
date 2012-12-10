from unittest import TestCase, main
from tranny.parser import parse_season, parse_release

class ReleaseTest(TestCase):
    release_a = 'The.Mentalist.S05E10.720p.HDTV.X264-DIMENSION'
    release_b = 'Homeland.S02E11.HDTV.x264-EVOLVE'
    release_c = 'Falcon.1x04.The.Silent.And.The.Damned.Part.Two.HDTV.x264-FoV'

    def test_parse_season(self):
        self.assertTupleEqual((5, 10), parse_season(self.release_a))
        self.assertTupleEqual((2, 11), parse_season(self.release_b))
        self.assertTupleEqual((1, 4), parse_season(self.release_c))

    def test_parse_release(self):
        self.assertEqual("The.Mentalist", parse_release(self.release_a))
        self.assertEqual("Homeland", parse_release(self.release_b))
        self.assertEqual("Falcon", parse_release(self.release_c))

if __name__ == '__main__':
    main()
