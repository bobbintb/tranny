from unittest import main
from tests import TrannyTestCase, get_fixture
from tranny import parser, init_config

init_config(get_fixture("test_config.ini"))


class ReleaseTest(TrannyTestCase):
    release_a = 'The.Mentalist.S05E10.720p.HDTV.X264-DIMENSION'
    release_b = 'Homeland.S02E11.HDTV.x264-EVOLVE'
    release_c = 'Falcon.1x04.The.Silent.And.The.Damned.Part.Two.HDTV.x264-FoV'
    release_d = "Easy.Money.2010.LIMITED.DVDRip.XviD-VH-PROD"
    release_e = u'The Daily Show - Tom Cruise 2013-04-16 [HDTV - 2HD]'  # eztv

    def test_parse_season(self):
        test_data = [
            [{'season': 5, 'episode': 10}, self.release_a],
            [{'season': 2, 'episode': 11}, self.release_b],
            [{'season': 1, 'episode': 4}, self.release_c]
        ]
        for expected, release_name in test_data:
            self.assertDictContainsSubset(expected, parser.parse_release_info(release_name))

    def test_parse_release(self):
        test_data = [
            ["The.Mentalist", self.release_a],
            ["Homeland", self.release_b],
            ["Falcon", self.release_c],
            ["Easy.Money", self.release_d]
        ]
        for expected, release_name in test_data:
            self.assertEqual(expected, parser.parse_release(release_name))

    def test_match_release(self):
        test_data = [
            ["tv", self.release_a],
            [False, self.release_b],
            ["tv", self.release_c],
            [False, self.release_d]
        ]
        for expected, release_name in test_data:
            self.assertEqual(expected, parser.match_release(release_name))


if __name__ == '__main__':
    main()
