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

    def test_update_trakt_movie(self):
        key = datastore.MovieReleaseKey("Reservoir Dogs 1992 720p BRRip x264-x0r", "reservoir.dogs", 1992)
        movie_data1 = metadata.update_trakt(key)
        movie_data2 = metadata.update_trakt(key)
        self.assertEqual(movie_data1, movie_data2)


