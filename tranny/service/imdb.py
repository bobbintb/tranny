# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
from os.path import join
import re
from subprocess import check_call
from ftplib import FTP
from imdb.Character import Character
from imdb.utils import RolesList
from imdb import IMDb
from tranny import cache
from tranny import util
from tranny import constants
from tranny.app import config

log = logging.getLogger(__name__)

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
    if access_method.lower() == "false":
        access_method = "http"
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


_runtime_rx = re.compile(r"(?P<runtime>\d+)")


def find_runtime(run_times):
    """ Parse the runtimes list looking for a runtime. Assume 1st is correct and
    move on.

    :param run_times: IMDB runtimes eg: [u'USA:60::(with commercials)'...]
    :type run_times: list
    :return: 1st parsed runtime
    :rtype: int
    """
    for rt in run_times:
        match = _runtime_rx.search(rt)
        if match:
            return match.groupdict()['runtime']
    return None


@cache.cache_on_arguments()
def get_movie(movie_id):
    try:
        int(_parse_imdb_id(movie_id))
    except ValueError:
        data = get_movie_by_title(movie_id)
    else:
        data = get_movie_by_id(movie_id)
    info = {}
    if data:
        api_data = data.data
        info['imdb_id'] = data.movieID
        info['title'] = api_data['title']
        info['genres'] = api_data.get('genres', [])
        info['cover_url'] = api_data.get('cover url', "")
        info['director'] = []
        for person in api_data.get('director', []):
            try:
                info['director'].append({
                    'person_id': person.personID,
                    'name': "{}".format(person)
                })
            except Exception as err:
                pass
        info['cast'] = []
        for person in api_data.get('cast', []):
            try:
                if isinstance(person.currentRole, Character):
                    role = person.currentRole
                elif isinstance(person.currentRole, RolesList):
                    role = person.currentRole[0]
                else:
                    continue
                info['cast'].append({
                    'person': {
                        'name': "{}".format(person),
                        'person_id': person.personID
                    },
                    'role': {
                        'name': "{}".format(role),
                        'role_id': role.characterID
                    }
                })
            except Exception as err:
                pass
        kind = api_data.get('kind', False)
        if kind == "tv series":
            info["kind"] = constants.MEDIA_TV
            info["seasons"] = api_data["number of seasons"]
            try:
                info["year"] = api_data["series years"].split("-")[0]
            except IndexError:
                pass
        elif kind == "movie":
            info["kind"] = constants.MEDIA_MOVIE
        else:
            info["kind"] = constants.MEDIA_UNKNOWN
        info["rating"] = api_data.get("rating", None)
        info["votes"] = api_data.get("votes", 0)
        info["runtime"] = find_runtime(api_data.get("runtimes", []))
    return info


def get_movie_by_id(imdb_id):
    results = _imdb.get_movie(_parse_imdb_id(imdb_id))
    return results


def get_movie_by_title(title):
    results = _imdb.get_movie(title)
    return results


def fetch_database(output_dir):
    """ Scan the FTP sources for data sets to use and download them to a temp folder

    TODO Only download new data?

    :param output_dir: Path to mirror the files too
    :type output_dir: unicode
    :return: download success status
    :rtype: bool
    """
    hosts = [
        ["ftp.fu-berlin.de", "/pub/misc/movies/database/"],
        ["ftp.funet.fi", "/pub/mirrors/ftp.imdb.com/pub/"],
        ["ftp.sunet.se", "/pub/tv+movies/imdb/"]
    ]
    for host, root in hosts:
        try:
            ftp = FTP(host)
            ftp.set_debuglevel(1)
            ftp.login()
            ftp.cwd(root)
            files = ftp.nlst()
            for f in [f for f in files if f.endswith("gz")]:
                ftp.retrbinary("RETR {}".format(f), open(join(output_dir, f), 'wb').write)
        except Exception:
            log.exception("Failed to download database files")
        else:
            return True
    return False


def load_sql(download=True):
    """ Load the datasets into the database, optionally downloading the dataset before

    :param download: Download a fresh dataset?
    :type download: bool
    :return: Load status
    :rtype: bool
    """
    tmp_dir = join(config.config_path, 'imdb_temp')
    util.mkdirp(tmp_dir)
    if not download or fetch_database(tmp_dir):
        args = ['imdbpy2sql.py', '-d', tmp_dir, '-u', config.get_db_uri()]
        if 'sqlite' in config.get_db_uri():
            # SQLite is laughably slow without this flag making, Using it
            # makes it possibly the fasted to import
            args.append('--sqlite-transactions')
        log.debug("Executing: {}".format(" ".join(args)))
        ret_val = check_call(args)
        log.debug(ret_val)
