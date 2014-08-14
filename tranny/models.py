# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from tranny.extensions import db
from tranny.constants import ROLE_USER


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, user_name=None, password=None, role=ROLE_USER):
        self.user_name = user_name
        self.password = password
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


class Section(db.Model):
    __tablename__ = "section"

    section_id = db.Column(db.Integer, primary_key=True, nullable=False)
    section_name = db.Column(db.String(64), unique=True)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, section_name):
        self.section_name = section_name


class Source(db.Model):
    __tablename__ = "source"

    source_id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(64), unique=True)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, source_name):
        self.source_name = source_name


class DownloadEntity(db.Model):
    __tablename__ = 'downloads'

    entity_id = db.Column(db.Integer, primary_key=True)
    release_key = db.Column(db.String(255), unique=True)
    section_id = db.Column(db.Integer, db.ForeignKey(Section.section_id))
    release_name = db.Column(db.String(255))
    source_id = db.Column(db.Integer, db.ForeignKey(Source.source_id))
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, release_key, release_name, section_id, source_id):
        self.release_key = release_key
        self.release_name = release_name
        self.section_id = section_id
        self.source_id = source_id


# class CountryBlock(db.Model):
#     __tablename__ = 'country_block'

