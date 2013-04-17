from ConfigParser import NoSectionError, NoOptionError
from re import compile, I, match
from logging import getLogger
from tranny.util import contains

log = getLogger(__name__)

pattern_info = [
    compile(r"\b(?P<year>(19|20)\d{2}).(?P<month>\d{1,2}).(?P<day>\d{1,2})", I),
    compile(r"\bS?(?P<season>\d+)[xe](?P<episode>\d+)\b", I)
]

pattern_release = [
    compile(r"^(?P<name>.+?)\bS?\d+[xe]\d+.+?$", I),
    compile(r"^(?P<name>.+?)\b(?P<year>(19|20)\d{2})"),

]


def normalize(name):
    normalized = '.'.join(clean_split(name))
    return str(normalized)


def clean_split(string):
    return [p for p in string.replace(".", " ").split(" ") if p]


def find_config_section(release_name, prefix="section_"):
    """ Attempt to find the configuration section the release provided matches with.

    :param release_name:
    :type release_name: str
    :param prefix:
    :type prefix: str
    :return:
    :rtype: str, bool
    """
    from tranny import config

    if is_ignored(release_name):
        return False
    sections = config.find_sections(prefix)
    for section in sections:
        quality = find_quality(release_name)
        for key_type in [quality, "any"]:
            key = "shows_{0}".format(key_type)
            if not config.has_option(section, key):
                # Ignore undefined sections
                continue
            patterns = config.build_regex_fetch_list(section, key)
            for pattern in patterns:
                if match(pattern, release_name, I):
                    section_name = config.get_unique_section_name(section)
                    return section_name
    return False


def is_ignored(release_name, section_name="ignore"):
    """ Check if the release should be ignored no matter what other conditions are matched

    :param release_name: Release name to match against
    :type release_name: str
    :return: Ignored status
    :rtype: bool
    """
    from tranny import config

    release_name = release_name.lower()
    for key in config.options(section_name):
        try:
            value = config.get(section_name, key)
        except (NoSectionError, NoOptionError):
            continue
        if key.startswith("string"):
            if value.lower() in release_name:
                log.debug("Matched string ignore pattern {0} {1}".format(key, release_name))
                return True
        elif key.startswith("rx"):
            if match(value, release_name, I):
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
    if _is_hd(release_name):
        return "hd"
    else:
        return "sd"


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

    :param release_name: A full release string: Conan.2013.04.15.Chelsea.Handler.HDTV.x264-2HD
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

    :param release_name:
    :type release_name:
    :return: Matched release section
    :rtype: str, bool
    """
    log.debug("Finding Match: {0}".format(release_name))
    section = find_config_section(release_name)
    return section
