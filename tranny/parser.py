# -*- coding: utf-8 -*-
"""
File name parser/tokenizer functions
"""
from __future__ import unicode_literals, absolute_import
import logging
import re
from datetime import date, datetime
from fuzzywuzzy import fuzz
from guessit import guess_file_info
from imdb._exceptions import IMDbError
from tranny import app
from tranny import constants
from tranny.exceptions import ParseError
from tranny.service import rating
from tranny import net

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


def valid_year(release_info, none_is_cur_year=True, section_name="section_movies"):
    """ Check if a release name is too new based on parsed year

    :param none_is_cur_year: If no year is found, assume current year if set to true.
    Generally only applies to movies.
    :type none_is_cur_year: bool
    :param release_info: Release info instance
    :type release_info: ReleaseInfo
    :param section_name:
    :type section_name: unicode
    :return: Valid status
    :rtype: bool
    """
    release_year = release_info.get('year', None)
    if not release_year and none_is_cur_year:
        release_year = date.today().year
    elif not release_year:
        log.warning("Failed to find a valid year and no default was allowed: {0}".format(release_info))
        return False
    year_min = app.config.get_default(section_name, "year_min", 0, int)
    if year_min and release_year < year_min:
        log.debug("Release year is too old. Minimum {}, Found {}".format(year_min, release_year))
        return False
    year_max = app.config.get_default(section_name, "year_max", 0, int)
    if year_max and release_year > year_max:
        log.info("Release year is too new. Max: {}, Found {}".format(year_max, release_year))
        return False
    return True


def valid_score(release_info, section_name="section_movie"):
    """ Check services to determine if the release has a score within the
    accepted range defined in the config

    :param section_name: Config section key to use for value lookups
    :param release_info: Release info instance
    :type release_info: ReleaseInfo
    :return: Valid score status
    :rtype: bool
    """
    score_min = app.config.get_default(section_name, "score_min", 0, float)
    score_max = app.config.get_default(section_name, "score_max", 0, float)
    if not (score_min or score_max):
        return None
    score_votes = app.config.get_default(section_name, "score_votes", 0, int)
    found_score = rating.score(release_info.release_title_norm, min_votes=score_votes)
    return bool(found_score)


def is_movie(release_info, strict=True):
    """ Check the release to see if its a movie.

    :param release_info:
    :type release_info: ReleaseInfo
    :return:
    :rtype: bool
    """
    release_name = release_info.release_name.lower()

    # Remove obvious non-movies
    if any([n in release_info.release_name.lower() for n in ["hdtv", "pdtv"]]):
        return False

    if not isinstance(release_info.release_key, MovieReleaseKey):
        return False
    if release_info.media_type == constants.MEDIA_MOVIE:
        # we know enough to determine its a movie and exit early
        return True
    try:
        title = "{0}.{1}".format(release_info.release_title_norm, release_info.release_key.year)
        info = rating.imdb_info(title.replace(".", " "))
        if not info:
            raise ValueError()
        match_rating = fuzz.token_sort_ratio(
            normalize(info.data['title'].lower()), release_info.release_title_norm)
        if match_rating < 75:
            raise ParseError("Title match ratio too low: {}".format(match_rating))
    except ParseError as err:
        log.warn(err)
    except ValueError:
        log.warn("Received no data from IMDB source")
    except IMDbError:
        log.error("Could not connect to IMDB server")
    else:
        kind = info.get('kind', None)
        if kind in ["tv series"]:
            return False
        elif kind in ["movie", "video movie"]:
            return True
    log.warning("Skipped release due to inability to determine type: {0}".format(release_name))
    return False


def valid_size(torrent, section_name):
    """ Check that the release falls within any size constraints

    :param torrent: Torrent instance to check
    :type torrent: tranny.torrent.Torrent
    :param section_name: Config section key
    :type section_name: unicode
    """
    size_min = app.config.get_default(section_name, "size_min", 0, int)
    size_max = app.config.get_default(section_name, "size_max", 0, int)
    size = (torrent.size() / 1024.0) / 1024.0
    if size_min and size <= size_min:
        log.debug("Release size too small: {} MB".format(size))
        return False
    if size_max and size >= size_max:
        log.debug("Release size too large: {} MB".format(size))
        return False
    return True


def valid_movie(release_info, section_name="section_movie"):
    """ Run through the checks to determine if the movie passes all minimum filters
     as specified in the configuration

    :param release_info:
    :type release_info: ReleaseInfo
    :param section_name:
    :type section_name: unicode
    :return:
    :rtype:
    """
    if not is_movie(release_info):
        return False
    if not valid_year(release_info, section_name=section_name):
        return False
    score_is_valid = valid_score(release_info, section_name=section_name)
    if score_is_valid is not None and not not score_is_valid:
        return None
    return True


def valid_tv(release_info, section_name="section_tv"):
    """ Check the tv section for existence of the release name. Return false if the
    title cannot be matched to any of the filters in the section config

    :param release_info:
    :type release_info: ReleaseInfo
    :param section_name:
    :type section_name: unicode
    :return:
    :rtype:
    """
    quality = find_quality(release_info)
    for key_type in [quality, "any"]:
        key = "quality_{0}".format(key_type)
        if not app.config.has_option(section_name, key):
            # Ignore undefined sections
            continue
        patterns = app.config.build_regex_fetch_list(section_name, key)
        for pattern in patterns:
            if re.match(pattern, release_info.release_name, re.I):
                section_name = app.config.get_unique_section_name(section_name)
                return section_name
    return False


def validate_section(release_info, prefix="section_"):
    """ Attempt to find the configuration section the release provided matches with.

    :param release_info:
    :type release_info: ReleaseInfo
    :param prefix:
    :type prefix: unicode
    :return:
    :rtype: str, bool
    """
    if is_ignored(release_info):
        return False
    sections = app.config.find_sections(prefix)
    for section in sections:
        if section.lower() == "section_movies":
            if valid_movie(release_info):
                return section
        elif section.lower() == "section_tv":
            if valid_tv(release_info):
                return section
    return False


def is_ignored(release_info, section_name="ignore"):
    """ Check if the release should be ignored no matter what other conditions are matched

    :param section_name:
    :type section_name: unicode
    :param release_info: Release name to match against
    :type release_info: ReleaseInfo
    :return: release_info status
    :rtype: bool
    """
    release_name = release_info.release_name.lower()
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


def find_quality(release_info):
    """
    :param release_info: Release name to parse
    :type release_info: ReleaseInfo
    :return:
    :rtype: unicode
    """
    if _is_hd(release_info.release_name):
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
            continue
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


def parse_release(release_name, guess_type=None):
    """ Fetch just the release name title from the release name provided

    :param guess_type: Hint at the media type being parsed. values: movie, episode, None
    :type guess_type: unicode
    :param release_name: A full release string Conan.2013.04.15.Chelsea.Handler.HDTV.x264-2HD
    :type release_name: unicode, unicode
    :return: Parsed release info instance
    :rtype: ReleaseInfo
    """
    # Guessit sucks when you don't have an extension, so we add .fake for those without
    try:
        try:
            if guess_type == 'tv':
                guess_type = 'episode'
            options = {
                'name_only': True,
                'type': guess_type
            }
            file_info = guess_file_info(normalize(release_name), options=options)
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
    """
    Common structure for info parsed from a release name. Use the guessit or internal factory functions
    depending on if guessit parsed the release properly
    """

    def __init__(self, release_name, guess_info, **kwargs):
        super(ReleaseInfo, self).__init__(**guess_info)
        self['release_name'] = release_name

    @classmethod
    def from_internal_parser(cls, release_name, title=None,
                             year=None, season=None, episode=None, day=None, month=None, media_type=None):
        """ Create a release info instance from internal parsers

        :param release_name: Full release name
        :param title: Parse release title
        :param year: Parsed year
        :param season: Parsed season
        :param episode: Parsed episode number
        :param day: Parsed episode day
        :param month: Parsed episode month
        :return: Configured ReleaseInfo instance
        :rtype: ReleaseInfo
        """
        ri_instance = cls(release_name, dict(
            title=title,
            year=year,
            season=season,
            episode=episode,
            day=day,
            month=month
        ))
        if media_type:
            ri_instance['type'] = media_type
        else:
            key = ri_instance.release_key
            if type(key) in [TVReleaseKey, TVDailyReleaseKey, TVSingleReleaseKey, TVSeasonReleaseKey]:
                ri_instance['type'] = constants.MEDIA_TV
            elif type(key) == MovieReleaseKey:
                ri_instance['type'] = constants.MEDIA_MOVIE
            else:
                ri_instance['type'] = constants.MEDIA_UNKNOWN
        if ri_instance['type'] in [constants.MEDIA_MOVIE, constants.MEDIA_UNKNOWN]:
            try:
                ri_instance.release_key.year
            except ParseError:
                year = find_year(ri_instance.release_name)
                if year:
                    ri_instance['year'] = year
                else:
                    raise ParseError("Cannot determine release type")
        return ri_instance

    @classmethod
    def from_guessit(cls, release_name, guess_info):
        """ Generate a ReleaseInfo instance from a guessit result set

        :param release_name: Full release name
        :param guess_info: Guess instance returned from guessit library
        :type guess_info: Guess
        :return: :rtype:
        """
        args = dict()
        for key, value in guess_info.items():
            if key == 'series':
                args['title'] = value
            elif key == 'episodeNumber':
                args['episode'] = value
            elif key == 'type':
                if value == 'episode':
                    args[key] = constants.MEDIA_TV
                elif value == 'movie':
                    args[key] = constants.MEDIA_MOVIE
                else:
                    args[key] = constants.MEDIA_UNKNOWN
            else:
                args[key] = value
        return cls(release_name, args)

    @property
    def media_type(self):
        return self.get('type', constants.MEDIA_UNKNOWN)

    @property
    def release_name(self):
        """ Simple shortcut """
        return self['release_name']

    @property
    def release_title_norm(self):
        """
        :return: Clean title useful for comparisons and key generation
        :rtype: unicode
        """
        return normalize(self['title']).lower()

    @property
    def is_proper(self):
        """
        :return: Is this release marked as a "proper"
        :rtype: bool
        """
        return ".proper." in self.release_name.lower()

    @property
    def is_repack(self):
        """
        :return: Is this release marked as a "proper"
        :rtype: bool
        """
        return ".repack." in self.release_name.lower()

    @property
    def release_key(self):
        """ Generate a comparable key used as a form of a primary key for a release
        to be used when comparing releases pulled from different sources as well as testing
        for existence internally.

        TODO: clean this up, use the guess['type'] keys better

        :return: Release key instance with parsed data loaded
        :rtype: BaseReleaseKey, TVReleaseKey, MovieReleaseKey, TVDailyReleaseKey, TVSingleReleaseKey
        :raise ParseError: Failed to find a suitable key format
        """
        if self.get('type', False) == constants.MEDIA_TV and self.get('date', False):
            # Daily broadcast episode
            release_key = TVDailyReleaseKey(self.release_name, self.release_title_norm,
                                            self['date'].day, self['date'].month, self['date'].year)
        elif self.get('type', False) == constants.MEDIA_TV:
            if self.get('season', False) and not self.get('episode'):
                # Season of show
                release_key = TVSeasonReleaseKey(
                    self.release_name, self.release_title_norm, self.get('season'), self.get('year', None))
            elif self.get('season', False) and self.get('episode', False):
                # Episode of season
                release_key = TVReleaseKey(self.release_name, self.release_title_norm,
                                           self['season'], self['episode'])
            else:
                week_num = datetime.now().isocalendar()[1]
                release_key = TVSingleReleaseKey(self.release_name, self.release_title_norm, week_num)
        elif self.get('type') == constants.MEDIA_MOVIE:
            year = self.get('year', None)
            if not year:
                year = find_year(self.release_name)
                if not year:
                    year = date.today().year
            release_key = MovieReleaseKey(self.release_name, self.release_title_norm, year)
        elif all([self.get('season', False), self.get('episode', False)]):
            # A single episode of a show
            release_key = TVReleaseKey(self.release_name, self.release_title_norm,
                                       self['season'], self['episode'])
        elif self.get('season', False) and not self.get('episode', False):
            # A season of a show
            release_key = TVSeasonReleaseKey(
                self.release_name, self.release_title_norm, self['season'], self.get('year', None))
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
        """ This only exists because the database will not try to coerce the key to unicode
        automatically, so we explicitly return the unicode value.

        .. note: unicode(self) will achieve the same result except the function does not exist in py3.3+

        :return: Release key as unicode
        :rtype: unicode
        """
        return "{}".format(self)


class TVReleaseKey(BaseReleaseKey):
    """
    Used for a standard tv episode with a season and episode number

    eg: Game.of.Kitties.S03E03.720p.HDTV.x264-XX
    """

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


class TVSeasonReleaseKey(BaseReleaseKey):
    """
    Used for a standard tv episode with a season and episode number

    eg: Game.of.Kitties.S03E03.720p.HDTV.x264-XX
    """

    def __init__(self, release_name, name, season, year=None):
        super(TVSeasonReleaseKey, self).__init__(
            release_name,
            name,
            "{}-{}".format(name, season),
            media_type=constants.MEDIA_TV
        )
        self.season = season
        self.year = year
        self.daily = False


class TVSingleReleaseKey(BaseReleaseKey):
    """
    Used for a show that does not use season/episode markers. This is far less reliable
    as a primary key than the other key classes since its much harder to parse correctly

    eg: F1.2012.Canadian.Grand.Prix.Qualifying.720p.HDTV.x264-XX
    """

    def __init__(self, release_name, name, show_title):
        super(TVSingleReleaseKey, self).__init__(
            release_name,
            name,
            "{}-{}".format(name, show_title),
            media_type=constants.MEDIA_TV
        )
        self.show_title = show_title


class TVDailyReleaseKey(BaseReleaseKey):
    """
    A show that uses date markers instead of season/episodes

    eg: Conan.2013.4.15.Chelsea.Handler.HDTV.x264-XX
    """

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
    """
    Key used for a movie release. Year is auto set to current year if not specified
    """
    def __init__(self, release_name, name, year):
        super(MovieReleaseKey, self).__init__(
            release_name,
            name,
            "{}-{}".format(name, year),
            media_type=constants.MEDIA_MOVIE
        )
        self.year = year
