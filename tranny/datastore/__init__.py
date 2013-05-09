from collections import defaultdict
import tranny
from tranny.util import contains
from tranny import parser
from tranny.models import User, DownloadEntity, Section, Source

cache_section = defaultdict(lambda: False)
cache_release = defaultdict(lambda: False)
cache_source = defaultdict(lambda: False)


def generate_release_key(release_name):
    """ Generate a key suitable for using as a database key value

    :param release_name: Release name to generate a key from
    :type release_name: str, unicode
    :return: Database suitable key name
    :rtype: str
    """
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


def get_section(section_name=None, section_id=None):
    if section_name:
        section = tranny.session.query(Section).filter_by(section_name=section_name).first()
    elif section_id:
        section = tranny.session.query(Section).filter_by(section_id=section_id).first()
    else:
        return tranny.session.query(Section).all()
    if not section and section_name:
        section = Section(section_name)
        tranny.session.add(section)
        tranny.session.commit()
    return section


def get_source(source_name=None, source_id=None):
    if source_name:
        source = cache_source[source_name]
        if not source:
            source = tranny.session.query(Source).filter_by(source_name=source_name).first()
            cache_source[source_name] = source
    elif source_id:
        for source in cache_source.itervalues():
            if source.source_id == source_id:
                break
        else:
            source = tranny.session.query(Source).filter_by(source_id=source_id).first()
            cache_source[source.source_name] = source
    else:
        return tranny.session.query(Source).all()
    if not source and source_name:
        source = Source(source_name)
        tranny.session.add(source)
        tranny.session.commit()
    elif not source:
        raise ValueError("Invalid source name")
    return source


def fetch_download(release_key=None, entity_id=None, limit=None):
    if release_key:
        data_set = tranny.session.query(DownloadEntity).filter_by(release_key=release_key).first()
    elif entity_id:
        data_set = tranny.session.query(DownloadEntity).filter_by(entity_id=entity_id).first()
    else:
        data_set = tranny.session.query(DownloadEntity).order_by(DownloadEntity.created_on.desc()).limit(limit).all()
    return data_set


def fetch_user(user_name=None, user_id=None, limit=None):
    """

    :param user_name:
    :type user_name:
    :param user_id:
    :type user_id:
    :param limit:
    :type limit:
    :return:
    :rtype: User, User[]
    """
    if user_name:
        data_set = tranny.session.query(User).filter_by(user_name=user_name).first()
    elif user_id:
        data_set = tranny.session.query(User).filter_by(user_id=user_id).first()
    else:
        data_set = tranny.session.query(User).limit(limit).all()
    return data_set
