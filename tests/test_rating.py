import unittest
from tests import get_fixture
from tranny import init_config

init_config(get_fixture("test_config.ini"))

# Make sure to import rating after config has been setup
from tranny.service import rating


class TestRating(unittest.TestCase):
    title_a = "The Mask"

    def test_imdb_score(self):
        self.assertTrue(rating._imdb_score(self.title_a) > 2.0)
        self.assertEqual(0, rating._imdb_score(self.title_a, min_votes=9999900))

    def test_tmdb_score(self):
        self.assertTrue(rating._tmdb_score(self.title_a) > 2.0)
        self.assertEqual(0, rating._imdb_score(self.title_a, min_votes=9999900))

    def test_score(self):
        self.assertTrue(rating.score(self.title_a) > 2.0)

