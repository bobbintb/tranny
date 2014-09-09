# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from testcase import TrannyTestCase
from tranny.service import trakt


class TraktServiceTest(TrannyTestCase):
    show = 'seinfeld'
    season = 3
    episode = 1
    tvrage_id = 5145
    movie = 'Reservoir Dogs'
    imdb_id = 'tt0105236'

    def test_show_summary(self):
        # Uses title with space to test slug detection
        self.assertEqual(trakt.show_summary("The Simpsons").get('tvrage_id', 0), 6190)

    def test_show_related(self):
        self.assertTrue(len(trakt.show_related(self.show)) >= 10)

    def test_show_season(self):
        season = trakt.show_season(self.show, self.season)
        self.assertTrue(len(season) == 23)

    def test_show_seasons(self):
        seasons = trakt.show_seasons(self.show)
        self.assertEqual(len(seasons), 10)

    def test_show__episode_seen(self):
        result = trakt.show_episode_seen(304130, 'Seinfeld', 5, 7, imdb_id='tt0697739')
        self.assertEqual(result['status'], 'success')

    def test_show_episode_summary(self):
        summary = trakt.show_episode_summary(self.show, self.season, self.episode)
        self.assertEqual(summary.get('episode', {}).get('season', 0), self.season)
        self.assertEqual(summary.get('episode', {}).get('number', 0), self.episode)

    def test_calendar_shows(self):
        shows = trakt.calendar_shows()
        self.assertEqual(len(shows), 7)

    def test_calendar_premiers(self):
        premiers = trakt.calendar_premiers()
        self.assertTrue(len(premiers) > 0)

    def test_search_tv(self):
        result = trakt.search_tv(self.show)
        self.assertTrue(result)
        self.assertEqual(result['tvrage_id'], self.tvrage_id)

    def test_search_movie(self):
        result = trakt.search_movie(self.movie)
        self.assertTrue(result)
        self.assertEqual(result['imdb_id'], self.imdb_id)

    def test_movie_summary(self):
        movie = trakt.movie_summary(self.movie)
        self.assertEqual(movie.get('imdb_id', ''), self.imdb_id)

    # These require a history on trakt, skip for now.
    # def test_recommend_movies(self):
    #     recommendations = trakt.recommend_movies()
    #    self.assertTrue(recommendations)

    # def test_recommend_shows(self):
    #    recommendations = trakt.recommend_shows()
    #    self.assertTrue(recommendations)
