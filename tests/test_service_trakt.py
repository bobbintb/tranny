# -*- coding: utf-8 -*-

from .testcase import TrannyTestCase, tapedeck
from tranny import constants
from tranny.service import trakt
from tranny.app import config


def strip_key(request):
    """ Remove API key before saving request to fixtures """
    api_key = config.get_default('service_trakt', 'api_key', "")
    request.uri = request.uri.replace(api_key, "X" * 20)
    return request


class TraktServiceTest(TrannyTestCase):
    show = 'seinfeld'
    season = 3
    episode = 1
    tvrage_id = 5145
    movie = 'Reservoir Dogs'
    imdb_id = 'tt0105236'

    def test_show_summary(self):
        # Uses title with space to test slug detection
        with tapedeck.use_cassette(self.track("test_show_summary"), before_record=strip_key):
            self.assertEqual(trakt.show_summary("The Simpsons", False).get('tvrage_id', 0), 6190, False)

    def test_show_related(self):
        with tapedeck.use_cassette(self.track("test_show_related"), before_record=strip_key):
            self.assertTrue(len(trakt.show_related(self.show)) >= 10)

    def test_show_season(self):
        with tapedeck.use_cassette(self.track("test_show_season"), before_record=strip_key):
            season = trakt.show_season(self.show, self.season)
        self.assertTrue(len(season) == 23)

    def test_show_seasons(self):
        with tapedeck.use_cassette(self.track("test_show_seasons"), before_record=strip_key):
            seasons = trakt.show_seasons(self.show)
        self.assertEqual(len(seasons), 10)

    # def test_show_episode_seen(self):
    #     result = trakt.show_episode_seen(304130, 'Seinfeld', 5, 7, imdb_id='tt0697739')
    #     self.assertEqual(result['status'], 'success')

    def test_show_episode_summary(self):
        with tapedeck.use_cassette(self.track("test_show_episode_summary_a"), before_record=strip_key):
            daily_summary = trakt.show_episode_summary_daily("The Daily Show", 9, 9, 2014)
        self.assertEqual(daily_summary['episode']['number'], 149)
        self.assertEqual(daily_summary['episode']['season'], 19)
        with tapedeck.use_cassette(self.track("test_show_episode_summary_b"), before_record=strip_key):
            summary = trakt.show_episode_summary(self.show, self.season, self.episode)
        self.assertEqual(summary.get('episode', {}).get('season', 0), self.season)
        self.assertEqual(summary.get('episode', {}).get('number', 0), self.episode)

    def test_calendar_shows(self):
        with tapedeck.use_cassette(self.track("test_calendar_shows"), before_record=strip_key):
            shows = trakt.calendar_shows(None, None)
        self.assertEqual(len(shows), 7)

    def test_calendar_premiers(self):
        with tapedeck.use_cassette(self.track("test_calendar_premiers"), before_record=strip_key):
            premiers = trakt.calendar_premiers()
        self.assertTrue(len(premiers) > 0)

    def test_search_episode(self):
        with tapedeck.use_cassette(self.track("test_search_episode"), before_record=strip_key):
            results = trakt.search_episode("The Daily Show - 2014-09-09")
        self.assertTrue(results)

    def test_search_tv(self):
        with tapedeck.use_cassette(self.track("test_search_tv"), before_record=strip_key):
            result = trakt.search_tv(self.show)
        self.assertTrue(result)
        self.assertEqual(result['tvrage_id'], self.tvrage_id)

    def test_search_movie(self):
        with tapedeck.use_cassette(self.track("test_search_movie"), before_record=strip_key):
            result = trakt.search_movie(self.movie)
        self.assertTrue(result)
        self.assertEqual(result['imdb_id'], self.imdb_id)

    def test_movie_summary(self):
        with tapedeck.use_cassette(self.track("test_movie_summary"), before_record=strip_key):
            movie = trakt.movie_summary(self.movie)
        self.assertEqual(movie.get('imdb_id', ''), self.imdb_id)

    def test_find_slug(self):
        items = [["Shortland Street",  73983]]
        i = 0
        for title, slug in items:
            with tapedeck.use_cassette(self.track("test_find_slug_{}".format(i)), before_record=strip_key):
                found_slug = trakt._find_slug(title, constants.MEDIA_TV)
            self.assertEqual(slug, found_slug, title)
            i += 1

    # These require a history on trakt, skip for now.
    # def test_recommend_movies(self):
    #     recommendations = trakt.recommend_movies()
    #    self.assertTrue(recommendations)

    # def test_recommend_shows(self):
    #    recommendations = trakt.recommend_shows()
    #    self.assertTrue(recommendations)
