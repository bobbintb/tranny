from re import compile, I
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

def find_section(name):
    pass

def is_ignored(name):
    pass

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
    return False
