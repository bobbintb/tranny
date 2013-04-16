from ConfigParser import NoSectionError, NoOptionError
from re import compile, I, match
from logging import getLogger

log = getLogger(__name__)

pattern_season = [
    compile(r"\bS?(?P<s>\d+)[xe](?P<e>\d+)\b", I)
]

pattern_release = [
    compile(r"^(?P<name>.+?)\bS?\d+[xe]\d+.+?$", I),
    compile(r"^(?P<name>.+?)\b(19\d{2}|20[12]\d)")
]


def normalize(name):
    normalized = '.'.join(clean_split(name))
    return normalized


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


def parse_season(release_name):
    for pattern in pattern_season:
        match = pattern.search(release_name, I)
        if match:
            values = match.groupdict()
            return int(values['s']), int(values['e'])
    return False


def parse_release(release_name):
    for pattern in pattern_release:
        match = pattern.search(release_name)
        if match:
            return normalize(match.groupdict()['name'])
    return False


def match_release(release_name):
    log.debug("Finding Match: {0}".format(release_name))
    section = find_config_section(release_name)
    return section
