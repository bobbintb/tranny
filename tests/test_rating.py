import unittest
from tests import get_fixture
from tranny import init_config

init_config(get_fixture("test_config.ini"))

# Make sure to import rating after config has been setup
from tranny import rating


class TestRating(unittest.TestCase):
    title_a = "The Mask"

    def test_get_imdb_score(self):
        score = rating.get_imdb_score(self.title_a)
        self.assertTrue(score > 2.0)

    def test_get_tmdb_score(self):
        score = rating.get_tmdb_score(self.title_a)
        self.assertTrue(score > 2.0)

    def test_get_score(self):
        score = rating.get_score(self.title_a)
        self.assertTrue(score > 2.0)

