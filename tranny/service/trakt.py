# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from functools import partial
from tranny import net, constants, util
from tranny.app import config

_slug_cache = {
    constants.MEDIA_MOVIE: {},
    constants.MEDIA_TV: {}
}


def _find_slug(title, media_type):
    slug = _slug_cache[media_type].get(title, None)
    if slug:
        return slug
    else:
        closest = search(title, media_type)
        if media_type == constants.MEDIA_MOVIE:
            slug = closest['imdb_id']
        elif media_type == constants.MEDIA_TV:
            slug = closest['tvdb_id']
        else:
            return title
        if slug:
            _slug_cache[media_type][title] = slug
        return slug


def _make_slug(title):
    return "-".join(title.lower().split(" "))


def _make_url(method, api_key):
    return "http://api.trakt.tv/{}.json/{}".format(method, api_key)


def _make_request(method, *args):
    key = config.get_default('trakt', 'api_key', None)
    if not key:
        return {}
    full_url = "".join([_make_url(method, key), '/' if args else "", '/'.join(map(unicode, args))])
    return net.fetch_url(full_url)


def calendar_shows():
    return _make_request('calendar/shows')


def calendar_premiers():
    return _make_request('calendar/premieres')


def search(search_query, media_type):
    if media_type == constants.MEDIA_TV:
        method = 'search/shows'
    else:
        method = 'search/movies'
    results = _make_request(method, search_query)
    return util.find_closest_match(search_query, results, 'title')


search_tv = partial(search, media_type=constants.MEDIA_TV)

search_movie = partial(search, media_type=constants.MEDIA_MOVIE)


def show_episode_summary(show, season, episode):
    return _make_request('show/episode/summary', _find_slug(show, constants.MEDIA_TV), season, episode)


def show_related(show):
    return _make_request('show/related', _find_slug(show, constants.MEDIA_TV))


def show_season(show, season):
    return _make_request('show/season', _find_slug(show, constants.MEDIA_TV), season)


def show_seasons(show):
    return _make_request('show/seasons', _find_slug(show, constants.MEDIA_TV))


def show_summary(show):
    return _make_request('show/summary', _find_slug(show, constants.MEDIA_TV))


def movie_summary(movie):
    return _make_request('movie/summary', _find_slug(movie, constants.MEDIA_MOVIE))


def movie_related(movie):
    return _make_request('movie/related', _find_slug(movie, constants.MEDIA_MOVIE))


def recommend_movies():
    return _make_request('recommendations/movies')


def recommend_shows():
    return _make_request('recommendations/shows')
