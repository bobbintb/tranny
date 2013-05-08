import datetime
from sqlalchemy import Column, Integer, String,  ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CreatedOnMixin(object):
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    updated_on = Column(DateTime, default=datetime.datetime.utcnow)


class User(CreatedOnMixin, Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(32))
    password = Column(String(60))

    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password

    def __repr__(self):
        return "<User('{0}','{1}')>".format(self.user_name, self.password)


class Section(CreatedOnMixin, Base):
    __tablename__ = "section"
    section_id = Column(Integer, primary_key=True)
    section_name = Column(String(64), unique=True)

    def __init__(self, section_name):
        self.section_name = section_name


class Source(CreatedOnMixin, Base):
    __tablename__ = "source"
    source_id = Column(Integer, primary_key=True)
    source_name = Column(String(64), unique=True)

    def __init__(self, source_name):
        self.source_name = source_name


class DownloadEntity(CreatedOnMixin, Base):
    __tablename__ = 'downloads'

    entity_id = Column(Integer, primary_key=True)
    release_key = Column(String(255), unique=True)
    section_id = Column(Integer, ForeignKey('section.section_id'))
    release_name = Column(String(255))
    source_id = Column(Integer, ForeignKey('source.source_id'))

    def __init__(self, release_key, release_name, section_id, source_id):
        self.release_key = release_key
        self.release_name = release_name
        self.section_id = section_id
        self.source_id = source_id
