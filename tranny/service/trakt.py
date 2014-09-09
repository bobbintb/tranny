# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from functools import partial
import time
import re
import hashlib
from tranny import net, constants, util
from tranny.app import config

_slug_cache = {
    constants.MEDIA_MOVIE: {},
    constants.MEDIA_TV: {}
}

TRAKT_URL = 'http://api.trakt.tv/'


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

slug_replace = partial(re.compile(r'[!@#$%^*\(\)\[\]\{\}/=?+\\|\-_]').sub, '')


def _make_slug(title):
    title = slug_replace(title).replace('&', 'and').replace(' ', '-')
    return "-".join(title.lower().split(" "))


def _make_url(method, api_key, json=True):
    return "{}{}{}/{}".format(TRAKT_URL, method, '.json' if json else '', api_key)


def _get_request(method, *args):
    key = config.get_default('trakt', 'api_key', None)
    if not key:
        return {}
    full_url = "".join([_make_url(method, key), '/' if args else "", '/'.join(map(unicode, args))])
    return net.http_request(full_url)


def _post_request(method, data):
    key = config.get_default('trakt', 'api_key', None)
    if not key:
        return {}
    username = config.get("trakt", "username")
    password = config.get("trakt", "password")
    url = _make_url(method, key, json=False)
    data['username'] = username
    data['password'] = hashlib.sha1(password).hexdigest()
    return net.http_request(url, data=data, method='post')


def calendar_shows():
    return _get_request('calendar/shows')


def calendar_premiers():
    return _get_request('calendar/premieres')


def search(search_query, media_type):
    if media_type == constants.MEDIA_TV:
        method = 'search/shows'
    else:
        method = 'search/movies'
    results = _get_request(method, search_query)
    return util.find_closest_match(search_query, results, 'title')


search_tv = partial(search, media_type=constants.MEDIA_TV)
search_movie = partial(search, media_type=constants.MEDIA_MOVIE)


def show_episode_summary(show, season, episode):
    return _get_request('show/episode/summary', _find_slug(show, constants.MEDIA_TV), season, episode)


def show_related(show):
    return _get_request('show/related', _find_slug(show, constants.MEDIA_TV))


def show_season(show, season):
    return _get_request('show/season', _find_slug(show, constants.MEDIA_TV), season)


def show_seasons(show):
    return _get_request('show/seasons', _find_slug(show, constants.MEDIA_TV))


def show_summary(show):
    return _get_request('show/summary', _find_slug(show, constants.MEDIA_TV))


def show_episode_seen(tvdb_id, title, season, episode, year=None, imdb_id=None):
    return _post_request(
        'show/episode/seen', {
            'tvdb_id': tvdb_id,
            'title': title,
            'year': year,
            'imdb_id': imdb_id,
            'episodes': [
                {
                    "season": season,
                    "episode": episode,
                    "last_played": time.time()
                }
            ]
        }
    )


def movie_summary(movie):
    return _get_request('movie/summary', _find_slug(movie, constants.MEDIA_MOVIE))


def movie_related(movie):
    return _get_request('movie/related', _find_slug(movie, constants.MEDIA_MOVIE))


def recommend_movies():
    return _get_request('recommendations/movies')


def recommend_shows():
    return _get_request('recommendations/shows')
