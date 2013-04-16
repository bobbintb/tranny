from tranny import parser


def generate_release_key(release_name):
    """ Generate a key suitable for using as a database key value

    :param release_name: Release name to generate a key from
    :type release_name: str
    :return: Database suitable key name
    :rtype: str
    """
    name = parser.parse_release(release_name)
    if not name:
        return False
    name = name.lower()
    try:
        season, episode = parser.parse_season(release_name)
    except TypeError:
        # Doesnt contain season/episode identifiers, treat as movie
        pass
    else:
        if season and episode:
            name = "{0}-{1}_{2}".format(name, season, episode)
    finally:
        return str(name)
