from ConfigParser import NoSectionError, NoOptionError
from re import compile, I, match
from datetime import date
from .app import config, logger
from .util import contains
from .service import rating


pattern_info = [
    compile(r"\b(?P<year>(19|20)\d{2}).(?P<month>\d{1,2}).(?P<day>\d{1,2})", I),
    compile(r"\bS?(?P<season>\d+)[xe](?P<episode>\d+)\b", I)
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
    normalized = '.'.join(clean_split(name))
    return str(normalized)


def clean_split(string):
    return [p for p in string.replace(".", " ").split(" ") if p]


def valid_year(config, release_name, none_is_cur_year=True, section_name="section_movies"):
    """ Check if a release name is too new

    :param none_is_cur_year: If no year is found, assume current year
    :type none_is_cur_year: bool
    :param config:
    :type config: tranny.configuration.Configuration
    :param release_name:
    :type release_name:
    :param section_name:
    :type section_name:
    :return:
    :rtype:
    """
    release_year = find_year(release_name)
    if not release_year and none_is_cur_year:
        release_year = date.today().year
    elif not release_year:
        logger.warning("Failed to find a valid year and no default was allowed: {0}".format(release_name))
        return False
    try:
        year_min = config.get_default(section_name, "year_min", 0, int)
    except (NoOptionError, NoSectionError, ValueError):
        year_min = 0
    if year_min and release_year < year_min:
        # Too old
        return False
    try:
        year_max = config.get_default(section_name, "year_max", 0, int)
    except (NoOptionError, NoSectionError, ValueError):
        year_max = 0

    if year_max and release_year > year_max:
        # Too new
        return False
    return True


def valid_score(config, release_name, section_name="section_movies"):
    release_name = parse_release(release_name)
    try:
        score_min = config.get_default(section_name, "score_min", 0, int)
    except (NoOptionError, NoSectionError, ValueError):
        score_min = 0
    try:
        score_max = config.get_default(section_name, "score_max", 0, int)
    except (NoOptionError, NoSectionError, ValueError):
        score_max = 0
    if not (score_min and score_max and release_name):
        return False
    try:
        score_votes = config.get_default(section_name, "score_votes", 0, int)
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

    title = parse_release(release_name)

    # Add a year to the name, helps with imdb quite a bit
    year = find_year(release_name)
    if year:
        title = "{0}.{1}".format(title, year)
    info = rating.imdb_info(title)
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
    logger.warning("Skipped release due to inability to determine type: {0}".format(release_name))
    return False


def valid_movie(config, release_name, section_name="section_movies"):
    """

    :param config:
    :type config: tranny.configuration.Configuration
    :param release_name:
    :type release_name:
    :return:
    :rtype:
    """
    if not is_movie(release_name):
        return False
    if not valid_year(config, release_name, section_name=section_name):
        return False
    if not valid_score(config, release_name, section_name=section_name):
        return False
    return True


def valid_tv(config, release_name, section_name="section_tv"):
    quality = find_quality(release_name)
    for key_type in [quality, "any"]:
        key = "quality_{0}".format(key_type)
        if not config.has_option(section_name, key):
            # Ignore undefined sections
            continue
        patterns = config.build_regex_fetch_list(section_name, key)
        for pattern in patterns:
            if match(pattern, release_name, I):
                section_name = config.get_unique_section_name(section_name)
                return section_name
    return False


def find_config_section(release_name, prefix="section_"):
    """ Attempt to find the configuration section the release provided matches with.

    :param release_name:
    :type release_name: str
    :param prefix:
    :type prefix: str
    :return:
    :rtype: str, bool
    """
    if is_ignored(release_name):
        return False
    sections = config.find_sections(prefix)
    for section in sections:
        if section.lower() == "section_movies":
            if valid_movie(config, release_name):
                return section
        elif section.lower() == "section_tv":
            if valid_tv(config, release_name):
                return section
    return False


def is_ignored(release_name, section_name="ignore"):
    """ Check if the release should be ignored no matter what other conditions are matched

    :param release_name: Release name to match against
    :type release_name: str
    :return: Ignored status
    :rtype: bool
    """
    release_name = release_name.lower()
    if any((pattern.match(release_name) for pattern in pattern_season)):
        return True
    for key in config.options(section_name):
        try:
            value = config.get(section_name, key)
        except (NoSectionError, NoOptionError):
            continue
        if key.startswith("string"):
            if value.lower() in release_name:
                logger.debug("Matched string ignore pattern {0} {1}".format(key, release_name))
                return True
        elif key.startswith("rx"):
            if match(value, release_name, I):
                logger.debug("Matched regex ignore pattern {0} {1}".format(key, release_name))
                return True
        else:
            logger.warning("Invalid ignore configuration key found: {0}".format(key))
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
    if _is_hd(release_name):
        return "hd"
    else:
        return "sd"


def find_year(release_name):
    for pattern in pattern_date:
        match = pattern.search(release_name, I)
        if not match:
            continue
        values = match.groupdict()
        try:
            return int(values['year'])
        except KeyError:
            pass
    return False


def parse_release_info(release_name):
    """ Parse release info out of the release name.

    :param release_name:
    :type release_name:
    :return:
    :rtype:
    """
    for pattern in pattern_info:
        match = pattern.search(release_name, I)
        if not match:
            continue
        values = match.groupdict()
        info = {}
        if contains(values, ["year", "month", "day"]):
            info = {
                'year': values['year'],
                'month': values['month'].zfill(2),
                'day': values['day'].zfill(2)
            }
        elif contains(values, ["season", "episode"]):
            info = {
                'season': int(values['season']),
                'episode': int(values['episode'])
            }
        return info
    return False


def parse_release(release_name):
    """ Fetch just the release name title from the release name provided

    :param release_name: A full release string Conan.2013.04.15.Chelsea.Handler.HDTV.x264-2HD
    :type release_name: str, unicode
    :return: Normalized release name found or False on no match
    :rtype: str, bool
    """
    for pattern in pattern_release:
        match = pattern.search(release_name)
        if match:
            return normalize(match.groupdict()['name'])
    return False


def match_release(release_name):
    """ Match a release to a section. Return the section found.

    :param config: App configuration instance
    :type config: tranny.configuration.Configuration
    :param release_name:
    :type release_name:
    :return: Matched release section
    :rtype: str, bool
    """
    logger.debug("Finding Match: {0}".format(release_name))
    section = find_config_section(release_name)
    if section == "movies":
        pass
    elif section == "tv":
        pass
    else:
        pass
    return section
