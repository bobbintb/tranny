# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tranny.service import imdb
from testcase import TrannyTestCase


class TestIMDB(TrannyTestCase):
    _id = "0094226"
    _title = "The Untouchables"

    def test_parse_imdb_id(self):
        self.assertEqual("12345", imdb._parse_imdb_id("tt12345"))
        self.assertEqual("12345", imdb._parse_imdb_id(12345))

    def test_get_movie_by_id(self):
        movie = imdb.get_movie_by_id(self._id)
        self.assertTrue(movie)

    def test_get_movie_by_title(self):
        movie = imdb.get_movie_by_title(self._title)
        self.assertTrue(movie)

    def test_get_movie(self):
        show = imdb.get_movie("tt1844624")
        show2 = imdb.get_movie("American Horror Story")
        self.assertEqual(show.movieID, show2.movieID)
