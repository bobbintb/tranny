# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from tranny import net
from tranny.app import config


def _make_url(method, api_key):
    return "http://api.trakt.tv/{}.json/{}".format(method, api_key)


def _make_request(method, *args):
    key = config.get_default('trakt', 'apikey', None)
    if not key:
        return {}
    return net.fetch_url(_make_url(method, key))


def calendar_shows():
    return _make_request('calendar/shows')


def calendar_premiers():
    return _make_request('calendar/premieres')


def search(search_query):
    return _make_request('search/shows', search_query)


def show_episode_summary(show, season, episode):
    return _make_request('show/episode/summary', show, season, episode)


def show_related(show):
    return _make_request('show/related', show)


def show_season(show, season):
    return _make_request('show/season', show, season)


def show_seasons(show):
    return _make_request('show/seasons', show)


def show_summary(show):
    return _make_request('show/summary', show)


def movie_summary(movie):
    return _make_request('movie/summary', movie)


def movie_related(movie):
    return _make_request('movie/related', movie)


def recommend_movies():
    return _make_request('recommendations/movies')


def recommend_shows():
    return _make_request('recommendations/shows')
