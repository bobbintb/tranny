from tranny.util import contains


class Datastore(object):
    def add(self, release_key, release_name, section=None, source=None):
        raise NotImplementedError("add() not implemented")

    def size(self):
        raise NotImplementedError("size() not implemented")

    def sync(self):
        return True

    def fetch(self, limit=25):
        raise NotImplementedError("fetch_newest() not implemented")


def generate_release_key(release_name):
    """ Generate a key suitable for using as a database key value

    :param release_name: Release name to generate a key from
    :type release_name: str, unicode
    :return: Database suitable key name
    :rtype: str
    """
    from tranny import parser

    release_name = parser.normalize(release_name)
    name = parser.parse_release(release_name)
    if not name:
        return False
    name = name.lower()
    try:
        info = parser.parse_release_info(release_name)
    except TypeError:
        # No release info parsed use default value for key: name
        pass
    else:
        if info:
            if contains(info, ["season", "episode"]):
                name = "{0}-{1}_{2}".format(name, info['season'], info['episode'])
            elif contains(info, ["year", "day", "month"]):
                name = "{0}-{1}_{2}_{3}".format(name, info['year'], info['month'], info['day'])
    finally:
        return name
