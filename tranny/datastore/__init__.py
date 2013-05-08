import tranny
from tranny.util import contains
from tranny import parser
from tranny.models import User, DownloadEntity, Section, Source


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
    if not section:
        section = Section(section_name)
        tranny.session.add(section)
        tranny.session.commit()
    return section


def get_source(source_name=None, source_id=None):
    if source_name:
        source = tranny.session.query(Source).filter_by(source_name=source_name).first()
    elif source_id:
        source = tranny.session.query(Source).filter_by(source_id=source_id).first()
    else:
        return tranny.session.query(Source).all()
    if not source:
        source = Source(source_name)
        tranny.session.add(source)
        tranny.session.commit()
    return source


def fetch_download(release_key=None, entity_id=None, limit=None):
    if release_key:
        data_set = tranny.session.query(DownloadEntity).filter_by(release_key=release_key).first()
    elif entity_id:
        data_set = tranny.session.query(DownloadEntity).filter_by(entity_id=entity_id).first()
    else:
        data_set = tranny.session.query(DownloadEntity).limit(limit).all()
    return data_set
