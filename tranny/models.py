# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import datetime
import hashlib
from sqlalchemy import CheckConstraint, Column, Integer, String, SmallInteger, DateTime, ForeignKey, Unicode, Table, \
    UnicodeText, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import BigInteger
from tranny.app import Base
from tranny.constants import ROLE_USER


class ModelArgs(object):
    @classmethod
    def build_model_or_args(cls, keys, data):
        """
        This method will build a list of sqlalchemy or_ parameters for the keys
        that exist in the dict that is assigned to the properties of the sub-classed
        model with the same name as the key.

        :param keys:
        :type keys:
        :param data:
        :type data:
        :return:[]or_
        :rtype:
        """
        show_args = []
        for key in keys:
            value = data.get(key, None)
            if value:
                show_args.append(getattr(cls, key) == value)
        return show_args


class PropUpdate(object):
    def update_properties(self, property_map, data):
        for model_prop, api_prop in property_map:
            api_value = data.get(api_prop, None)
            if not api_value:
                continue
            setattr(self, model_prop, api_value)
        return self


class GenreUpdate(object):
    def update_genres(self, session, genres):
        from tranny.datastore import get_genre
        for genre in [g.title() for g in genres]:
            if not self.genres or not genre in [g.genre_name for g in self.genres]:
                new_genre = get_genre(session, genre, create=True)
                if new_genre:
                    self.genres.append(new_genre)


class User(Base, ModelArgs):
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
        # TODO How to properly convert int to unicode for py3?
        return "{}".format(self.user_id)


class Section(Base, ModelArgs):
    __tablename__ = "section"

    section_id = Column(Integer, primary_key=True, nullable=False)
    section_name = Column(String(64), unique=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    updated_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, section_name):
        self.section_name = section_name


class Source(Base, ModelArgs):
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

person_movie_director_assoc_table = Table(
    'person_movie_director',
    Base.metadata,
    Column('person_id', Integer, ForeignKey("person.person_id")),
    Column("movie_id", Integer, ForeignKey("movie.movie_id"))
)

person_movie_cast_assoc_table = Table(
    'person_movie_cast',
    Base.metadata,
    Column('person_id', Integer, ForeignKey("person.person_id")),
    Column("movie_id", Integer, ForeignKey("movie.movie_id"))
)

person_show_director_assoc_table = Table(
    'person_show_director',
    Base.metadata,
    Column('person_id', Integer, ForeignKey("person.person_id")),
    Column("show_id", Integer, ForeignKey("show.show_id"))
)


class Genre(Base, ModelArgs):
    __tablename__ = 'genre'

    genre_id = Column(Integer, primary_key=True)
    genre_name = Column(Unicode(length=16), unique=True, nullable=False)

    def __init__(self, genre_name=None):
        if genre_name:
            self.genre_name = genre_name.title()


class MediaInfo(Base, ModelArgs):
    __tablename__ = 'media_info'

    media_id = Column(Integer, primary_key=True)
    media_type = Column(Unicode, nullable=False)
    imdb_id = Column(Integer, nullable=True)
    tvdb_id = Column(Integer, nullable=True)
    tmdb_id = Column(Integer, nullable=True)
    tvrage_id = Column(Integer, nullable=True)


class Show(Base, ModelArgs, PropUpdate, GenreUpdate):
    __tablename__ = 'show'

    external_keys = ['imdb_id', 'tvrage_id', 'tvdb_id']

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


class Episode(Base, ModelArgs, PropUpdate):
    __tablename__ = 'episode'

    external_keys = ['imdb_id', 'tvdb_id']

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

    show = relationship("Show")


class Movie(Base, ModelArgs, PropUpdate, GenreUpdate):
    __tablename__ = 'movie'

    external_keys = ['tvdb_id', 'imdb_id']

    movie_id = Column(Integer, primary_key=True)
    title = Column(Unicode(length=255), nullable=False)
    year = Column(Integer, CheckConstraint('year > 1900 AND year < 2050'))
    released = Column(Integer)
    trakt_url = Column(Unicode(length=255))
    cover_url = Column(Unicode(255), nullable=True)
    trailer = Column(Unicode(length=255))
    runtime = Column(Integer)
    tag_line = Column(UnicodeText)
    imdb_id = Column(Unicode(length=10), unique=True, nullable=True)
    tmdb_id = Column(Integer, unique=True, nullable=True)
    rt_id = Column(Integer, unique=True, nullable=True)
    imdb_score = Column(Numeric(asdecimal=False), default=0.0)
    imdb_votes = Column(Integer, default=0)

    genres = relationship('Genre', secondary=genre_movie_assoc_table, backref="movies")
    directors = relationship('Person', secondary=person_movie_director_assoc_table, backref="movies")
    cast = relationship('Person', secondary=person_movie_cast_assoc_table, backref="cast")


class Person(Base):
    __tablename__ = "person"

    person_id = Column(Integer, primary_key=True)
    imdb_person_id = Column(Integer, nullable=False, unique=True)
    name = Column(Unicode(length=255), nullable=False)

    def __init__(self, imdb_person_id, name=None):
        self.imdb_person_id = imdb_person_id
        self.name = name


class Download(Base, ModelArgs):
    __tablename__ = 'download'

    entity_id = Column(Integer, primary_key=True)
    release_key = Column(String(255), unique=True)
    section_id = Column(Integer, ForeignKey(Section.section_id))
    release_name = Column(String(255))
    source_id = Column(Integer, ForeignKey(Source.source_id))
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    updated_on = Column(DateTime, default=datetime.datetime.utcnow)
    media_id = Column(Integer, ForeignKey(MediaInfo.media_id))

    source = relationship(Source, lazy='joined')
    section = relationship(Section, lazy='joined')

    def __init__(self, release_key, release_name, section_id, source_id):
        self.release_key = release_key
        self.release_name = release_name
        self.section_id = section_id
        self.source_id = source_id


class GeoIP(Base):
    """
    1:1 Mapping of geolite database
    """
    __tablename__ = 'geoip'

    range_id = Column(Integer, primary_key=True)
    ip_start = Column(BigInteger, nullable=False)
    ip_end = Column(BigInteger, nullable=False)
    country = Column(Unicode(length=100), nullable=False)
    code = Column(Unicode(length=2), nullable=False)

    def __init__(self, ip_start, ip_end, code, country):
        self.ip_start = int(ip_start)
        self.ip_end = int(ip_end)
        self.code = code
        self.country = country
