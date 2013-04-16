from re import compile, I, match
from logging import getLogger

log = getLogger(__name__)

pattern_season = [
    compile(r"\bS?(?P<s>\d+)[xe](?P<e>\d+)\b", I)
]

pattern_release = [
    compile(r"^(?P<name>.+?)\bS?\d+[xe]\d+.+?$", I)
]


def normalize(name):
    normalized = '.'.join(clean_split(name))
    return normalized


def clean_split(string):
    return [p for p in string.replace(".", " ").split(" ") if p]


def find_config_section(release_name, prefix="section_"):
    from tranny import config

    sections = config.find_sections(prefix)
    for section in sections:
        for key_type in ("hd", "sd", "any"):
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


def is_ignored(release_name):
    return False


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
