# -*- coding: utf-8 -*-
from unittest import main
from tranny import parser
from testcase import TrannyTestCase


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
            [False, "Teen.Wolf.1985.720P.BRRIP.XVID.AC3-MAJESTiC"],
            ["section_tv", self.release_a],
            [False, self.release_b],
            ["section_tv", self.release_c],
            [False, self.release_d],

        ]
        for expected, release_name in test_data:
            self.assertEqual(expected, parser.match_release(release_name), release_name)

    def test_find_date(self):
        test_data = [
            [False, self.release_a],
            [2010, self.release_d]
        ]
        self.run_data_set(test_data, parser.find_year)

    def test_is_movie(self):
        test_data = [
            [False, self.release_a],
            [False, self.release_b],
            [False, self.release_c],
            [True, self.release_d],
            [True, "Teen.Wolf.1985.720P.BRRIP.XVID.AC3-MAJESTiC"]
        ]
        for expected, release_name in test_data:
            self.assertEqual(expected, parser.is_movie(release_name), release_name)

    def test_is_ignored(self):
        test_data = [
            [True, 'Homeland.S02.HDTV.x264-EVOLVE'],
            [False, 'Homeland.S02E11.HDTV.x264-EVOLVE']
        ]
        self.run_data_set(test_data, parser.is_ignored)

if __name__ == '__main__':
    main()
