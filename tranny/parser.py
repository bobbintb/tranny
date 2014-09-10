# -*- coding: utf-8 -*-
"""
File name parser/tokenizer functions
"""
from __future__ import unicode_literals
from ConfigParser import NoSectionError, NoOptionError
from re import compile, I, match
from datetime import date
from tranny import app
from tranny.service import rating


pattern_info = [
    compile(r"\b(?P<year>(19|20)\d{2}).(?P<month>\d{1,2}).(?P<day>\d{1,2})", I),
    compile(r"\bS?(?P<season>\d+)[xe](?P<episode>\d+)\b", I),
    compile(r"\b(?P<year>(19|20)\d{2}).", I)
]

pattern_release = [
    compile(r"^(?P<name>.+?)\bS?\d+[xe]\d+.+?$", I),
    compile(r"^(?P<name>.+?)\b(?P<year>(19|20)\d{2})", I),
]

pattern_date = [
    compile(r"(?P<year>(19|20)\d{2})", I)
]

pattern_season = [
    compile(r"[\.\s]s\d{1,2}[\.\s]", I)
]


def normalize(name):
    return str('.'.join(clean_split(name)))


def clean_split(string):
    return [p for p in string.replace(".", " ").split(" ") if p]


def valid_year(release_name, none_is_cur_year=True, section_name="section_movies"):
    """ Check if a release name is too new

    :param none_is_cur_year: If no year is found, assume current year
    :type none_is_cur_year: bool
    :param release_name:
    :type release_name: unicode
    :param section_name:
    :type section_name: unicode
    :return:
    :rtype:
    """
    release_year = find_year(release_name)
    if not release_year and none_is_cur_year:
        release_year = date.today().year
    elif not release_year:
        app.logger.warning("Failed to find a valid year and no default was allowed: {0}".format(release_name))
        return False
    try:
        year_min = app.config.get_default(section_name, "year_min", 0, int)
    except (NoOptionError, NoSectionError, ValueError):
        year_min = 0
    if year_min and release_year < year_min:
        # Too old
        return False
    try:
        year_max = app.config.get_default(section_name, "year_max", 0, int)
    except (NoOptionError, NoSectionError, ValueError):
        year_max = 0

    if year_max and release_year > year_max:
        # Too new
        return False
    return True


def valid_score(release_name, section_name="section_movies"):
    """

    :type release_name: unicode
    :type section_name: unicode
    :return:
    :rtype: bool, None
    """
    release_name = parse_release(release_name)
    if not release_name:
        return None
    try:
        score_min = app.config.get_default(section_name, "score_min", 0, int)
    except (NoOptionError, NoSectionError, ValueError):
        score_min = 0
    try:
        score_max = app.config.get_default(section_name, "score_max", 0, int)
    except (NoOptionError, NoSectionError, ValueError):
        score_max = 0
    if not (score_min and score_max and release_name):
        return False
    try:
        score_votes = app.config.get_default(section_name, "score_votes", 0, int)
    except (NoOptionError, NoSectionError, ValueError):
        score_votes = 0
    if release_name:
        found_score = rating.score(release_name, min_votes=score_votes)
        return bool(found_score)
    return False


def is_movie(release_name, strict=True):
    """ Check the release to see if its a movie.

    :param release_name:
    :type release_name:
    :return:
    :rtype:
    """
    release_name = release_name.lower()

    # Remove obvious non-movies
    if any([n in release_name for n in ["hdtv"]]):
        return False

    orig_title = parse_release(release_name)

    # Add a year to the name, helps with imdb quite a bit
    year = find_year(release_name)
    if year:
        title = "{0}.{1}".format(orig_title, year)
        info = rating.imdb_info(title.replace(".", " "))
    else:
        info = rating.imdb_info(orig_title.replace(".", " "))
    if info:
        try:
            kind = info['kind']
        except KeyError:
            pass
        else:
            if kind in ["tv series"]:
                return False
            elif kind in ["movie", "video movie"]:
                return True
    else:
        try:
            info = rating.tmdb_info(orig_title.replace(".", " "))
        except:
            pass
        else:
            if info:
                return True
    app.logger.warning("Skipped release due to inability to determine type: {0}".format(release_name))
    return False


def valid_movie(release_name, section_name="section_movies"):
    """

    :param release_name:
    :type release_name: unicode
    :param section_name:
    :type section_name: unicode
    :return:
    :rtype:
    """
    if not is_movie(release_name):
        return False
    if not valid_year(release_name, section_name=section_name):
        return False
    if not valid_score(release_name, section_name=section_name):
        return False
    return True


def valid_tv(release_name, section_name="section_tv"):
    """

    :param release_name:
    :type release_name: unicode
    :param section_name:
    :type section_name: unicode
    :return:
    :rtype:
    """
    quality = find_quality(release_name)
    for key_type in [quality, "any"]:
        key = "quality_{0}".format(key_type)
        if not app.config.has_option(section_name, key):
            # Ignore undefined sections
            continue
        patterns = app.config.build_regex_fetch_list(section_name, key)
        for pattern in patterns:
            if match(pattern, release_name, I):
                section_name = app.config.get_unique_section_name(section_name)
                return section_name
    return False


def find_section(release_name, prefix="section_"):
    """ Attempt to find the configuration section the release provided matches with.

    :param release_name:
    :type release_name: unicode
    :param prefix:
    :type prefix: unicode
    :return:
    :rtype: str, bool
    """
    if is_ignored(release_name):
        return False
    sections = app.config.find_sections(prefix)
    for section in sections:
        if section.lower() == "section_movies":
            if valid_movie(release_name):
                return section
        elif section.lower() == "section_tv":
            if valid_tv(release_name):
                return section
    return False


def is_ignored(release_name, section_name="ignore"):
    """ Check if the release should be ignored no matter what other conditions are matched

    :param section_name:
    :type section_name: unicode
    :param release_name: Release name to match against
    :type release_name: unicode
    :return: Ignored status
    :rtype: bool
    """
    release_name = release_name.lower()
    if any((pattern.search(release_name) for pattern in pattern_season)):
        return True
    for key in app.config.options(section_name):
        try:
            value = app.config.get(section_name, key)
        except (NoSectionError, NoOptionError):
            continue
        if key.startswith("string"):
            if value.lower() in release_name:
                app.logger.debug("Matched string ignore pattern {0} {1}".format(key, release_name))
                return True
        elif key.startswith("rx"):
            if match(value, release_name, I):
                app.logger.debug("Matched regex ignore pattern {0} {1}".format(key, release_name))
                return True
        else:
            app.logger.warning("Invalid ignore configuration key found: {0}".format(key))
    return False


# (?!.*(720|1080)p).+?\.HDTV.(XviD|x264)
def _is_hd(release_name):
    """ Determine if a release is classified as high-definition

    :param release_name: release name to parse
    :type release_name: basestring
    :return: high-def status
    :rtype: bool
    """
    if "720" in release_name or "1080" in release_name:
        return True
    return False


def _is_sd(release_name):
    if "HDTV" in release_name:
        return True
    return False


def find_quality(release_name):
    """
    :param release_name: Release name to parse
    :type release_name: unicode
    :return:
    :rtype: unicode
    """
    if _is_hd(release_name):
        return "hd"
    else:
        return "sd"


def find_year(release_name):
    """ Parse a year value from a string and return it

    :param release_name: Release name to parse
    :type release_name: unicode
    :return: Parsed year
    :rtype: int, bool
    """
    for pattern in pattern_date:
        p_match = pattern.search(release_name, I)
        if not p_match:
            continue
        values = p_match.groupdict()
        try:
            return int(values['year'])
        except KeyError:
            pass
    return False


def parse_release_info(release_name):
    """ Parse release info out of the release name.

    :param release_name:
    :type release_name: unicode
    :return:
    :rtype:
    """
    for pattern in pattern_info:
        p_match = pattern.search(release_name, I)
        if not p_match:
            continue
        values = p_match.groupdict()
        info = {}
        value_set = set(values.keys())
        if value_set == {"year", "month", "day"}:
            # Daily broadcast
            info = {
                'year': values['year'],
                'month': values['month'].zfill(2),
                'day': values['day'].zfill(2)
            }
        elif value_set == {"season", "episode"}:
            # Season broadcast
            info = {
                'season': int(values['season']),
                'episode': int(values['episode'])
            }
        elif value_set == {"year"}:
            info = {'year': int(values['year'])}
        return info
    return False

stop_words = set('hdtv')

def parse_release(release_name):
    """ Fetch just the release name title from the release name provided

    :param release_name: A full release string Conan.2013.04.15.Chelsea.Handler.HDTV.x264-2HD
    :type release_name: str, unicode
    :return: Normalized release name found or False on no match
    :rtype: unicode, bool
    """
    for pattern in pattern_release:
        p_match = pattern.search(release_name)
        if p_match:
            if p_match.lastgroup == "year":
                pass
            return normalize(p_match.groupdict()['name'])
    return False
