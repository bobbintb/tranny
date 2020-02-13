# -*- coding: utf-8 -*-

from .testcase import TrannyTestCase, get_fixture, tapedeck
from tranny.service import imdb


class TestIMDB(TrannyTestCase):
    _id = "0094226"
    _title = "The Untouchables"

    def test_parse_imdb_id(self):
        self.assertEqual("12345", imdb._parse_imdb_id("tt12345"))
        self.assertEqual("12345", imdb._parse_imdb_id(12345))

    def test_get_movie_by_id(self):
        with tapedeck.use_cassette('test_get_movie_by_id.json'):
            movie = imdb.get_movie_by_id(self._id)
        self.assertEqual(self._id, movie.movieID)

    def test_get_movie_by_title(self):
        movie = imdb.get_movie_by_title(self._title)
        self.assertTrue(movie)

    def test_get_movie(self):
        show = imdb.get_movie("tt1844624")
        print((dir(show)))
        show2 = imdb.get_movie("American Horror Story")
        self.assertEqual(show['imdb_id'], show2['imdb_id'])
