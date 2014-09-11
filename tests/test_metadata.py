# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from testcase import TrannyTestCase
from tranny import metadata, datastore


class MetaDataTest(TrannyTestCase):

    def test_update_trakt_show(self):
        key = datastore.TVReleaseKey("The.Simpsons.S10E11.720p.HDTV.x264-GRP", "the.simpsons", 10, 11)
        tv_data1 = metadata.update_trakt(key)
        tv_data2 = metadata.update_trakt(key)
        self.assertEqual(tv_data1, tv_data2)
        self.assertTrue(len(tv_data2.show.genres) >= 2)

        key2 = datastore.TVDailyReleaseKey("The.Daily.Show.2014.07.31.Aubrey.Plaza.HDTV.x264-BATV.mp4", "the.daily.show", 31, 7, 2014)
        tv_data3 = metadata.update_trakt(key2)
        tv_data4 = metadata.update_trakt(key2)
        self.assertEqual(tv_data3, tv_data4)
        self.assertTrue(len(tv_data4.show.genres) >= 3)

    def test_update_trakt_movie(self):
        key = datastore.MovieReleaseKey("Reservoir Dogs 1992 720p BRRip x264-x0r", "reservoir.dogs", 1992)
        movie_data1 = metadata.update_trakt(key)
        movie_data2 = metadata.update_trakt(key)
        self.assertEqual(movie_data1, movie_data2)
        self.assertTrue(len(movie_data1.genres) >= 2)


