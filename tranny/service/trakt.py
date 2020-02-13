# -*- coding: utf-8 -*-

from functools import partial
import re
import hashlib
from fuzzywuzzy import fuzz
from tranny import net
from tranny import constants
from tranny import util
from tranny import cache
from tranny.app import config

_slug_cache = {
    constants.MEDIA_MOVIE: {},
    constants.MEDIA_TV: {}
}

TRAKT_URL = 'http://api.trakt.tv/'

show_properties_map = [
    # [Model.prop, api.prop]
    ['air_day', 'air_day'],
    ['air_time', 'air_time'],
    ['certification', 'certification'],
    ['imdb_id', 'imdb_id'],
    ['tvdb_id', 'tvdb_id'],
    ['tvrage_id', 'tvrage_id'],
    ['title', 'title'],
    ['year', 'year'],
    ['trakt_url', 'url'],
    ['first_aired', 'first_aired_utc'],
    ['country', 'country'],
    ['overview', 'overview'],
    ['runtime', 'runtime'],
    ['network', 'network']
]

episode_property_map = [
    # [Model.prop, api.prop]
    ['first_aired', 'first_aired'],
    ['trakt_url', 'url'],
    ['overview', 'overview'],
    ['title', 'title'],
    ['tvdb_id', 'tvdb_id'],
    ['imdb_id', 'imdb_id'],
    ['number', 'number'],
    ['season', 'season']
]

movie_property_map = [
    # [Model.prop, api.prop]
    ['title', 'title'],
    ['year', 'year'],
    ['released', 'released'],
    ['trakt_url', 'url'],
    ['trailer', 'trailer'],
    ['runtime', 'runtime'],
    ['tag_line', 'tagline'],
    ['imdb_id', 'imdb_id'],
    ['tmdb_id', 'tmdb_id'],
    ['rt_id', 'rt_id']
]


@cache.cache_on_arguments(expiration_time=3600*7)
def _find_slug(title, media_type):
    slug = _slug_cache[media_type].get(title, None)
    if slug:
        return slug
    else:
        closest = search(media_type, title)
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


def _get_request(method, *args, **kwargs):
    params = kwargs.get('params', None)
    args = [i for i in args if i]
    key = config.get_default('service_trakt', 'api_key', None)
    if not key:
        return {}
    full_url = "".join([_make_url(method, key), '/' if args else "", '/'.join(map(str, args))])
    return net.http_request(full_url, params=params, method='get')


def _post_request(method, data):
    key = config.get_default('service_trakt', 'api_key', None)
    if not key:
        return {}
    username = config.get("service_trakt", "username")
    password = config.get("service_trakt", "password")
    url = _make_url(method, key, json=False)
    data['username'] = username
    data['password'] = hashlib.sha1(password).hexdigest()
    results = net.http_request(url, data=data, method='post')
    return results


@cache.cache_on_arguments(expiration_time=3600)
def calendar_shows(date, days):
    return _get_request('calendar/shows', date, days)


@cache.cache_on_arguments(expiration_time=3600)
def calendar_premiers():
    return _get_request('calendar/premieres')


#@cache.cache_on_arguments()
def search(media_type, search_query):
    if media_type == constants.MEDIA_TV:
        method = 'search/shows'
    else:
        method = 'search/movies'
    results = _get_request(method, search_query)
    if not results:
        return results
    try:
        return util.find_closest_match(search_query, results, 'title')
    except IndexError as err:
        return None


search_tv = partial(search, constants.MEDIA_TV)
search_movie = partial(search, constants.MEDIA_MOVIE)


def search_episode(search_query):
    results = _get_request('search/episodes', params={'query': search_query})
    return results


@cache.cache_on_arguments()
def show_episode_summary(show, season, episode):
    return _get_request('show/episode/summary', _find_slug(show, constants.MEDIA_TV), season, episode)


@cache.cache_on_arguments()
def show_episode_summary_daily(show, day, month, year):
    date_fmt = "{}{:0>2}{:0>2}".format(year, month, day)
    shows = calendar_shows(date_fmt, 1)
    if not shows or not shows[0].get('episodes', None):
        return {}
    best_match = [0, None]
    for show_info in shows[0].get('episodes', []):
        show_data = show_info.get('show', {})
        ratio = fuzz.partial_ratio(show, show_data.get('title', ""))
        if ratio > best_match[0]:
            best_match = [ratio, show_info]
    return best_match[1]


@cache.cache_on_arguments()
def show_related(show):
    return _get_request('show/related', _find_slug(show, constants.MEDIA_TV))


@cache.cache_on_arguments()
def show_season(show, season):
    return _get_request('show/season', _find_slug(show, constants.MEDIA_TV), season)


@cache.cache_on_arguments()
def show_seasons(show):
    return _get_request('show/seasons', _find_slug(show, constants.MEDIA_TV))


@cache.cache_on_arguments()
def show_summary(show, extended):
    args = [_find_slug(show, constants.MEDIA_TV)]
    if extended:
        args.append("extended")
    return _get_request('show/summary', *args)


@cache.cache_on_arguments()
def movie_summary(movie):
    return _get_request('movie/summary', _find_slug(movie, constants.MEDIA_MOVIE))


@cache.cache_on_arguments()
def movie_related(movie):
    return _get_request('movie/related', _find_slug(movie, constants.MEDIA_MOVIE))


@cache.cache_on_arguments()
def recommend_movies():
    return _get_request('recommendations/movies')


@cache.cache_on_arguments()
def recommend_shows():
    return _get_request('recommendations/shows')
