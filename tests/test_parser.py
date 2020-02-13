# -*- coding: utf-8 -*-
"""
Tests for the parser module
"""

from datetime import datetime, date
import unittest
from .testcase import TrannyTestCase, get_fixture
from tranny import parser
from tranny import constants
from tranny.app import config
from tranny.torrent import Torrent


class ReleaseTest(TrannyTestCase):
    release_a = 'The.Mentalist.S05E10.720p.HDTV.X264-DIMENSION'
    release_b = 'Homeland.S02E11.HDTV.x264-EVOLVE'
    release_c = 'Falcon.1x04.The.Silent.And.The.Damned.Part.Two.HDTV.x264-FoV'
    release_d = "Easy.Money.2010.LIMITED.DVDRip.XviD-VH-PROD"
    release_e = 'The Daily Show - Tom Cruise 2013-04-16 [HDTV - 2HD]'  # eztv
    release_f = "Teen.Wolf.1985.720P.BRRIP.XVID.AC3-MAJESTiC"
    release_g = "Homeland.S02.HDTV.x264-EVOLVE"

    def test_parse_season(self):
        test_data = [
            [{'season': 5, 'episode': 10}, self.release_a],
            [{'season': 2, 'episode': 11}, self.release_b],
            [{'season': 1, 'episode': 4}, self.release_c]
        ]
        for expected, release_name in test_data:
            self.assertDictContainsSubset(expected, parser.parse_release_info(release_name))

    def test_validate_section(self):
        test_data = [
            ["section_tv", self.release_a, {'title': 'The.Mentalist', 'episode': 10, 'season': 2}],
            ["section_tv", self.release_c, {'title': 'Falcon', 'episode': 4, 'season': 1}],
            [False, "Teen.Wolf.1985.720P.BRRIP.XVID.AC3-MAJESTiC", {'title': 'Teen.Wolf', 'year': 1985}],
            [False, self.release_b, {'title': 'Homeland', 'episode': 11, 'season': 2}],
            [False, self.release_d, {'title': 'Easy.Money', 'year': 2010}],

        ]
        config.set("filter_ignore", "string11", "blahhh") # fix other test causing this to fail, fix later
        for params in test_data:
            release_info = parser.ReleaseInfo.from_internal_parser(params[1], **params[2])
            found_section = parser.validate_section(release_info)
            self.assertEqual(params[0], found_section, "{} -> {}".format(params[1], found_section))

    def test_find_date(self):
        test_data = [
            [False, self.release_a],
            [2010, self.release_d]
        ]
        self.run_data_set(test_data, parser.find_year)

    def test_is_movie(self):
        test_data = [
            [False, self.release_a, {'title': 'The.Mentalist', 'episode': 10, 'season': 2}],
            [False, self.release_b, {'title': 'Homeland', 'episode': 11, 'season': 2}],
            [False, self.release_c, {'title': 'Falcon', 'episode': 4, 'season': 1}],
            [False, self.release_b, {'title': 'The.Daily.Show', 'day': 16, 'month': 4, 'year': 2013}],
            [True, self.release_d, {'title': 'Easy.Money', 'year': 2010}],
            [True, self.release_f, {'title': 'Teen.Wolf', 'year': 1985}],
            [False, self.release_g, {'title': 'Homeland', 'season': 2}]
        ]
        for params in test_data:
            release_info = parser.ReleaseInfo.from_internal_parser(params[1], **params[2])
            self.assertEqual(params[0], parser.is_movie(release_info), params[1])
        fake_release_info = parser.ReleaseInfo.from_internal_parser(
            "Homeland.S02E11.HDTV.x264-EVOLVE",
            **{'title': 'homeland', 'year': 1985, 'media_type': constants.MEDIA_MOVIE}
        )
        self.assertFalse(parser.is_movie(fake_release_info))

    @unittest.skipUnless(config.getboolean("service_imdb", "enabled"), "IMDB not enabled")
    def test_is_movie_lookup(self):
        release_info = parser.ReleaseInfo.from_internal_parser(
            "Teen.Wolf.1985.720P.BRRIP.XVID.AC3-MAJESTiC",
            **{'title': 'teen.wolf', 'year': 1985, 'media_type': constants.MEDIA_UNKNOWN}
        )
        self.assertTrue(parser.is_movie(release_info))

        release_info_2 = parser.ReleaseInfo.from_internal_parser(
            "Teen.Wolf.1985.720P.BRRIP.XVID.AC3-MAJESTiC",
            **{'title': 'teen.wolf', 'media_type': constants.MEDIA_UNKNOWN}
        )
        self.assertTrue(parser.is_movie(release_info_2))

        release_info_2 = parser.ReleaseInfo.from_internal_parser(
            "BS.MOVIE.TITLE.BLARG.1985.720P.BRRIP.XVID.AC3-MAJESTiC",
            **{'title': 'bs.movie.title.blarg', 'media_type': constants.MEDIA_UNKNOWN}
        )
        self.assertFalse(parser.is_movie(release_info_2))

        release_info_2 = parser.ReleaseInfo.from_internal_parser(
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.1985.720P.BRRIP.XVID.AC3-MAJESTiC",
            **{'title': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'media_type': constants.MEDIA_UNKNOWN}
        )
        self.assertFalse(parser.is_movie(release_info_2))

    def test_is_ignored(self):
        test_data = [
            [True, 'Homeland.S02.HDTV.x264-EVOLVE', {'title': 'Homeland', 'season': 2}],
            [False, 'Homeland.S02E11.HDTV.x264-EVOLVE', {'title': 'Homeland', 'episode': 11, 'season': 2}]
        ]
        for params in test_data:
            release_info = parser.ReleaseInfo.from_internal_parser(params[1], **params[2])
            self.assertEqual(params[0], parser.is_ignored(release_info))

        rls = parser.ReleaseInfo.from_internal_parser(
            'The.Mentalist.S05E10.720p.HDTV.X264-DIMENSION',
            **{'title': 'The.Mentalist', 'episode': 10, 'season': 2})
        config.set("filter_ignore", "string10", "test")
        self.assertFalse(parser.is_ignored(rls))
        config.set("filter_ignore", "string11", "mental")
        self.assertTrue(parser.is_ignored(rls))

    def test_parse_release(self):
        args = [
            ["f1-{}".format(datetime.now().isocalendar()[1]),
             "F1.2012.Canadian.Grand.Prix.Qualifying.720p.HDTV.x264-XX", parser.TVSingleReleaseKey],
            ["first.snow-2006", 'First Snow 2006 BRRip XvidHD 720p-XX', parser.MovieReleaseKey],
            ["conan-2013_04_15", "Conan.2013.4.15.Chelsea.Handler.HDTV.x264-XX", parser.TVDailyReleaseKey],
            ["conan-2013_04_15", "Conan.2013.04.15.Chelsea.Handler.HDTV.x264-XX", parser.TVDailyReleaseKey],
            ["game.of.kitties-3_3", "Game.of.Kitties.S03E03.720p.HDTV.x264-XX", parser.TVReleaseKey],
            ["homeland-2", "Homeland.S02.HDTV.x264-EVOLVE", parser.TVSeasonReleaseKey],
        ]
        for i in args:
            release = parser.parse_release(i[1])
            self.assertEqual(release.release_key, i[0])
            self.assertEqual(type(release.release_key), i[2])

    def test_valid_year(self):
        release_info = parser.ReleaseInfo.from_internal_parser(
            "Teen.Wolf.1985.720P.BRRIP.XVID.AC3-MAJESTiC",
            **{'title': 'teen.wolf', 'year': 1985, 'media_type': constants.MEDIA_MOVIE}
        )
        section_name = "section_movie"
        config.set(section_name, "year_min", 1985)
        self.assertTrue(parser.valid_year(release_info, section_name=section_name))

        config.set(section_name, "year_min", 1986)
        self.assertFalse(parser.valid_year(release_info, section_name=section_name))

        config.set(section_name, "year_min", 1965)
        config.set(section_name, "year_max", 1985)
        self.assertTrue(parser.valid_year(release_info, section_name=section_name))

        config.set(section_name, "year_max", 1984)
        self.assertFalse(parser.valid_year(release_info, section_name=section_name))

        release_info_2 = parser.ReleaseInfo.from_internal_parser(
            "Teen.Wolf.1985.720P.BRRIP.XVID.AC3-MAJESTiC",
            **{'title': 'teen.wolf', 'media_type': constants.MEDIA_MOVIE}
        )
        config.set(section_name, "year_min", date.today().year)
        config.set(section_name, "year_max", 0)
        self.assertTrue(parser.valid_year(release_info_2, section_name=section_name))

        config.set(section_name, "year_min", date.today().year+1)
        self.assertFalse(parser.valid_year(release_info_2, section_name=section_name))

        self.assertFalse(parser.valid_year(release_info_2, section_name=section_name, none_is_cur_year=False))

    def test_valid_movie(self):
        release_info_1 = parser.ReleaseInfo.from_internal_parser(
            "Teen.Wolf.1985.720P.BRRIP.XVID.AC3-MAJESTiC",
            **{'title': 'teen.wolf', 'media_type': constants.MEDIA_MOVIE}
        )
        section_name = "section_movie"
        config.set(section_name, "year_min", 0)
        config.set(section_name, "year_max", 0)
        self.assertTrue(parser.valid_movie(release_info_1))

    @unittest.skipUnless(config.getboolean("service_imdb", "enabled"), "IMDB not enabled")
    def test_valid_movie_lookup(self):
        release_info_1 = parser.ReleaseInfo.from_internal_parser(
            "Teen.Wolf.1985.720P.BRRIP.XVID.AC3-MAJESTiC",
            **{'title': 'teen.wolf', 'media_type': constants.MEDIA_MOVIE}
        )
        section_name = "section_movie"
        config.set(section_name, "year_min", 0)
        config.set(section_name, "year_max", 0)
        config.set(section_name, "score_min", 1)
        self.assertTrue(parser.valid_movie(release_info_1))

    def test_valid_size(self):
        t = Torrent.from_file(get_fixture("linux-iso.torrent"))
        section_name = "section_movie"
        config.set(section_name, "size_min", 1)
        config.set(section_name, "size_max", 10000)
        self.assertTrue(parser.valid_size(t, section_name))

        config.set(section_name, "size_max", 400)
        self.assertFalse(parser.valid_size(t, section_name))

        config.set(section_name, "size_min", 7000)
        config.set(section_name, "size_max", 10000)
        self.assertFalse(parser.valid_size(t, section_name))
