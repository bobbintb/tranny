# -*- coding: utf-8 -*-
"""
File name parser/tokenizer functions
"""
from __future__ import unicode_literals, absolute_import
import logging
from guessit import guess_file_info
import re
from imdb._exceptions import IMDbDataAccessError
from datetime import date, datetime
from tranny import app
from tranny import constants
from tranny.exceptions import ParseError
from tranny.service import rating

log = logging.getLogger(__name__)

pattern_info = [
    re.compile(r"\b(?P<year>(19|20)\d{2}).(?P<month>\d{1,2}).(?P<day>\d{1,2})", re.I),
    re.compile(r"\bS?(?P<season>\d+)[xe](?P<episode>\d+)\b", re.I),
    re.compile(r"\b(?P<year>(19|20)\d{2}).", re.I)
]

pattern_release = [
    re.compile(r"^(?P<title>.+?)\bS?\d+[xe]\d+.+?$", re.I),
    re.compile(r"^(?P<title>.+?)\b(?P<year>(19|20)\d{2})", re.I),
]

pattern_date = [
    re.compile(r"(?P<year>(19|20)\d{2})", re.I)
]

pattern_season = [
    re.compile(r"[\.\s]s\d{1,2}[\.\s]", re.I)
]


def normalize(name):
    return '.'.join(clean_split(name))


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
        log.warning("Failed to find a valid year and no default was allowed: {0}".format(release_name))
        return False
    year_min = app.config.get_default(section_name, "year_min", 0, int)
    if year_min and release_year < year_min:
        log.debug("Release year is too old. Minimum {}, Found {}".format(year_min, release_year))
        return False
    year_max = app.config.get_default(section_name, "year_max", 0, int)
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
    score_min = app.config.get_default(section_name, "score_min", 0, float)
    score_max = app.config.get_default(section_name, "score_max", 0, float)
    if not (score_min and score_max and release_name):
        return False
    score_votes = app.config.get_default(section_name, "score_votes", 0, int)
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
    if any([n in release_name for n in ["hdtv", "pdtv"]]):
        return False

    orig_title = parse_release(release_name)

    # Add a year to the name, helps with imdb quite a bit
    year = find_year(release_name)
    try:
        if year:
            title = "{0}.{1}".format(orig_title, year)
            info = rating.imdb_info(title.replace(".", " "))
        else:
            info = rating.imdb_info(orig_title.replace(".", " "))
    except IMDbDataAccessError:
        log.error("Could not connect to IMDB server")
    else:
        if info:
            kind = info.get('kind', None)
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
    log.warning("Skipped release due to inability to determine type: {0}".format(release_name))
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
            if re.match(pattern, release_name, re.I):
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
        value = app.config.get_default(section_name, key, None)
        if value is None:
            continue
        if key.startswith("string"):
            if value.lower() in release_name:
                log.debug("Matched string ignore pattern {0} {1}".format(key, release_name))
                return True
        elif key.startswith("rx"):
            if re.match(value, release_name, re.I):
                log.debug("Matched regex ignore pattern {0} {1}".format(key, release_name))
                return True
        else:
            log.warning("Invalid ignore configuration key found: {0}".format(key))
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
        p_match = pattern.search(release_name, re.I)
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
    :return: Parsed release info
    :rtype: dict
    """
    for pattern in pattern_info:
        p_match = pattern.search(release_name, re.I)
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
    :type release_name: unicode, unicode
    :return: Parsed release info instance
    :rtype: ReleaseInfo
    """
    # Guessit sucks when you don't have an extension, so we add .fake for those without
    try:
        try:
            file_info = guess_file_info(normalize(release_name), options={'name_only': True})
        except AttributeError:
            file_info = {}
        if not file_info or file_info.get('type', 'unknown') == 'unknown':
            _name = normalize(release_name)
            for pattern in pattern_release:
                p_match = pattern.search(_name)
                if p_match:
                    parsed_title = normalize(p_match.groupdict()['title'])
                    parsed_info = parse_release_info(_name)
                    if not parsed_title and parsed_info:
                        continue
                    info = ReleaseInfo.from_internal_parser(release_name, parsed_title, **parsed_info)
                    break
            else:
                raise ValueError()
        else:
            info = ReleaseInfo.from_guessit(release_name, file_info)
    except ValueError:
        raise ParseError("Failed to parse release name: {}".format(release_name))
    return info

_has_ext = re.compile(r"\.\S{2,4}^", re.I)


def has_valid_ext(release_name):
    if _has_ext.match(release_name):
        return True
    return False


class ReleaseInfo(dict):
    def __init__(self, release_name, guess_info, **kwargs):
        super(ReleaseInfo, self).__init__(**guess_info)
        self['release_name'] = release_name

    @property
    def release_name(self):
        return self['release_name']

    @property
    def release_title_norm(self):
        return normalize(self['title']).lower()

    @classmethod
    def from_guessit(cls, release_name, guess_info):
        args = dict()
        for key, value in guess_info.items():
            if key == 'series':
                args['title'] = value
            elif key == 'episodeNumber':
                args['episode'] = value
            else:
                args[key] = value
        return cls(release_name, args)

    @classmethod
    def from_internal_parser(cls, release_name, title, year=None, season=None, episode=None, day=None, month=None):
        return cls(release_name, dict(
            title=title,
            year=year,
            season=season,
            episode=episode,
            day=day,
            month=month
        ))

    @property
    def release_key(self):
        if self.get('type', False) == "episode" and self.get('date', False):
            release_key = TVDailyReleaseKey(self.release_name, self.release_title_norm,
                                            self['date'].day, self['date'].month, self['date'].year)
        elif self.get('type', False) == "episode":
            release_key = TVReleaseKey(self.release_name, self.release_title_norm,
                                       self['season'], self['episode'])
        elif self.get('type') == "movie":
            # Very likely a  movie
            release_key = MovieReleaseKey(self.release_name, self.release_title_norm, self['year'])
        elif all([self.get('season', False), self.get('episode', False)]):
            release_key = TVReleaseKey(self.release_name, self.release_title_norm,
                                       self['season'], self['episode'])
        elif all([self.get('year', False), self.get('day', False), self.get('month', False)]):
            release_key = TVDailyReleaseKey(self.release_name, self.release_title_norm,
                                            self['day'], self['month'], self['year'])
        elif self.get("year", False):
            if any([k in self.release_name.lower() for k in ['hdtv', 'sdtv', 'pdtv', 'satrip']]):
                # assume tv if all params exist
                # TODO this needs something more robust since this will obviously not work in all cases.
                week_num = datetime.now().isocalendar()[1]
                release_key = TVSingleReleaseKey(self.release_name, self.release_title_norm, week_num)
            else:
                # assume movie as fallback
                release_key = MovieReleaseKey(self.release_name, self.release_title_norm, self['year'])
        else:
            raise ParseError("Cannot create release key")
        return release_key


class BaseReleaseKey(object):
    """
    Basic info for a release used to make a unique identifier for a release name
    """
    def __init__(self, release_name, name, release_key=None, media_type=constants.MEDIA_UNKNOWN):
        self.release_name = release_name
        self.name = name
        self.release_key = release_key or name
        self.media_type = media_type

    def __unicode__(self):
        return self.release_key

    def __str__(self):
        return self.release_key.encode("utf-8")

    def __eq__(self, other):
        return other == self.release_key

    def as_unicode(self):
        return "{}".format(self)


class TVReleaseKey(BaseReleaseKey):
    def __init__(self, release_name, name, season, episode, year=None):
        super(TVReleaseKey, self).__init__(
            release_name,
            name,
            "{}-{}_{}".format(name, season, episode),
            media_type=constants.MEDIA_TV
        )
        self.season = season
        self.episode = episode
        self.year = year
        self.daily = False


class TVSingleReleaseKey(BaseReleaseKey):
    def __init__(self, release_name, name, show_title):
        super(TVSingleReleaseKey, self).__init__(
            release_name,
            name,
            "{}-{}".format(name, show_title),
            media_type=constants.MEDIA_TV
        )
        self.show_title = show_title


class TVDailyReleaseKey(BaseReleaseKey):
    def __init__(self, release_name, name, day, month, year):
        super(TVDailyReleaseKey, self).__init__(
            release_name,
            name,
            release_key="{}-{}_{:0>2}_{:0>2}".format(name, year, month, day),
            media_type=constants.MEDIA_TV
        )
        self.day = day
        self.month = month
        self.year = year
        self.daily = True


class MovieReleaseKey(BaseReleaseKey):
    def __init__(self, release_name, name, year):
        super(MovieReleaseKey, self).__init__(
            release_name,
            name,
            "{}-{}".format(name, year),
            media_type=constants.MEDIA_MOVIE
        )
        self.year = year
