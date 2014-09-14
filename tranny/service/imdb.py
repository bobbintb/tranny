# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from imdb import IMDb
from tranny import cache
from tranny.app import config

config_section = 'service_imdb'


def _parse_imdb_id(imdb_id):
    """ Parse the int value from a imdb id format ttNNNNNN if the prefix is found
     on the input value. If the input is an int just return it.

     This method is used because if using the sql based imdb database it will expect an
     integer without the tt prefix. The http method will accept both so we default to
     always using the integer

    :param imdb_id:
    :type imdb_id:
    :return:
    :rtype:
    """
    if isinstance(imdb_id, int):
        imdb_id = "{}".format(imdb_id)
    if imdb_id.startswith("tt"):
        imdb_id = imdb_id[2:]
    return imdb_id


def _make_imdb():
    """ Configure and return the imdb object ready for use

    :return: Imdb instance for querying
    :rtype: IMDbBase
    """
    access_method = config.get_default(config_section, 'sql', 'http')
    kwargs = {}
    if access_method == 'sql':
        kwargs = {
            "uri": config.get('db', 'uri'),
            "useORM": "sqlalchemy"
        }

    i = IMDb(access_method, **kwargs)
    if access_method == "http":
        if config.getboolean("proxy", "enabled"):
            i.set_proxy(config.get_default("proxy", "server", ''))
    return i

_imdb = _make_imdb()


def get_movie(movie_id):
    try:
        int(_parse_imdb_id(movie_id))
    except ValueError:
        data = get_movie_by_title(movie_id)
    else:
        data = get_movie_by_id(movie_id)
    info = {}
    if data:
        api_data = data.get('data')
        info['title'] = api_data['title']
        info['genres'] = api_data['genres']
        info['cover_url'] = api_data['cover_url']
        info['director'] = []
        for person in api_data.get('director', []):
            info['director'].append({
                'person_id': api_data['personID'],
                'name': "{}".format(person)
            })
        info['cast'] = []
        for person in api_data.get('cast', []):
            info['cast'].append({
                'person': {
                    'name': "{}".format(person),
                    'person_id': person['personID']
                },
                'role': {
                    'name': "{}".format(person.currentRole[0]),
                    'role_id': person.currentRole[0].characterID
                }
            })
        if api_data['kind'] == "tv series":
            info["seasons"] = api_data["number of seasons"]
            try:
                info["year"] = api_data["series years"].split("-")[0]
            except IndexError:
                pass
        info["rating"] = api_data["rating"]

    return info




@cache.cache_on_arguments()
def get_movie_by_id(imdb_id):
    results = _imdb.get_movie(_parse_imdb_id(imdb_id))
    return results


@cache.cache_on_arguments()
def get_movie_by_title(title):
    results = _imdb.get_movie(title)
    return results
