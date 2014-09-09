# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import hashlib
from sqlalchemy import CheckConstraint, Column, Integer, String, SmallInteger, DateTime, ForeignKey, Unicode, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import UnicodeText
from tranny import constants
from tranny.app import Base
from tranny.constants import ROLE_USER


class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(32), nullable=False)
    password = Column(String(40), nullable=False)
    role = Column(SmallInteger, default=ROLE_USER)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    updated_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, user_name=None, password=None, role=ROLE_USER):
        self.user_name = user_name
        self.password = hashlib.sha1(password).hexdigest()
        self.role = role

    def __repr__(self):
        return "<User('{0}','{1}')>".format(self.user_name, self.password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return not self.user_id

    def get_id(self):
        return unicode(self.user_id)


class Section(Base):
    __tablename__ = "section"

    section_id = Column(Integer, primary_key=True, nullable=False)
    section_name = Column(String(64), unique=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    updated_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, section_name):
        self.section_name = section_name


class Source(Base):
    __tablename__ = "source"

    source_id = Column(Integer, primary_key=True)
    source_name = Column(String(64), unique=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    updated_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, source_name):
        self.source_name = source_name

genre_tv_assoc_table = Table(
    'show_genres',
    Base.metadata,
    Column('show_id', Integer, ForeignKey('show.show_id')),
    Column('genre_id', Integer, ForeignKey('genre.genre_id'))
)

genre_movie_assoc_table = Table(
    'movie_genres',
    Base.metadata,
    Column('movie_id', Integer, ForeignKey('movie.movie_id')),
    Column('genre_id', Integer, ForeignKey('genre.genre_id'))
)


class Genre(Base):
    __tablename__ = 'genre'

    genre_id = Column(Integer, primary_key=True)
    genre_name = Column(Unicode(length=16), unique=True, nullable=False)


class MediaInfo(Base):
    __tablename__ = 'media_info'

    media_id = Column(Integer, primary_key=True)
    media_type = Column(Integer, CheckConstraint('media_type = "{}" OR media_type = "{}"'.format(
        constants.MEDIA_TV, constants.MEDIA_MOVIE
    )))
    imdb_id = Column(Integer, nullable=True)
    tvdb_id = Column(Integer, nullable=True)
    # themovieorg ID
    tmdb_id = Column(Integer, nullable=True)
    tvrage_id = Column(Integer, nullable=True)


class Show(Base):
    __tablename__ = 'show'

    show_id = Column(Integer, primary_key=True)
    title = Column(Unicode(length=255), nullable=False)
    year = Column(Integer, CheckConstraint('year > 1900 AND year < 2050'))
    trakt_url = Column(Unicode(length=255))
    first_aired = Column(Integer)
    country = Column(Unicode(length=50))
    overview = Column(UnicodeText)
    runtime = Column(Integer)
    network = Column(Unicode(length=64))
    air_day = Column(Unicode(length=9))
    air_time = Column(Unicode(length=8))
    certification = Column(Unicode(length=32))
    imdb_id = Column(Unicode(length=10), unique=True, nullable=True)
    tvdb_id = Column(Integer, unique=True, nullable=True)
    tvrage_id = Column(Integer, unique=True, nullable=True)

    genres = relationship('Genre', secondary=genre_tv_assoc_table, backref="shows")
    episodes = relationship("Episode")


class Episode(Base):
    __tablename__ = 'episode'

    episode_id = Column(Integer, primary_key=True)
    show_id = Column(Integer, ForeignKey(Show.show_id))
    season = Column(Integer)
    number = Column(Integer)
    imdb_id = Column(Unicode(length=10), unique=True, nullable=True)
    tvdb_id = Column(Integer, unique=True, nullable=True)
    title = Column(Unicode(length=255), nullable=False)
    overview = Column(UnicodeText)
    trakt_url = Column(Unicode(length=255))
    first_aired = Column(Integer)


class Movie(Base):
    __tablename__ = 'movie'

    movie_id = Column(Integer, primary_key=True)
    title = Column(Unicode(length=255), nullable=False)
    year = Column(Integer, CheckConstraint('year > 1900 AND year < 2050'))
    released = Column(Integer)
    trakt_url = Column(Unicode(length=255))
    trailer = Column(Unicode(length=255))
    runtime = Column(Integer)
    tag_line = Column(UnicodeText)
    imdb_id = Column(Unicode(length=10), unique=True, nullable=True)
    tmdb_id = Column(Integer, unique=True, nullable=True)
    rt_id = Column(Integer, unique=True, nullable=True)

    genres = relationship('Genre', secondary=genre_movie_assoc_table, backref="movies")



class Download(Base):
    __tablename__ = 'download'

    entity_id = Column(Integer, primary_key=True)
    release_key = Column(String(255), unique=True)
    section_id = Column(Integer, ForeignKey(Section.section_id))
    release_name = Column(String(255))
    source_id = Column(Integer, ForeignKey(Source.source_id))
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    updated_on = Column(DateTime, default=datetime.datetime.utcnow)
    media_id = Column(Integer, ForeignKey(MediaInfo.media_id))

    def __init__(self, release_key, release_name, section_id, source_id):
        self.release_key = release_key
        self.release_name = release_name
        self.section_id = section_id
        self.source_id = source_id
