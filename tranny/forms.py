# -*- coding: utf-8 -*-
from os.path import join, dirname
from flask.ext.wtf import Form
from wtforms import HiddenField, SelectField, validators
from flask_wtf.file import FileField, FileAllowed, FileRequired

from flask.ext import uploads
from tranny import app

torrent_file_set = uploads.UploadSet(
    'torrent',
    extensions=['torrent'],
    default_dest=lambda p: join(dirname(__file__), 'uploads')
)


class UploadForm(Form):
    torrent_file = FileField("Torrent File", validators=[FileRequired(), FileAllowed(torrent_file_set)])
    section = SelectField("Section", validators=[validators.required()])
    next_url = HiddenField("Next URL", default="")

    @classmethod
    def make(cls):
        ul_form = cls()
        ul_form.section.choices = [[s[len("section_"):], s[len("section_"):]]
                                   for s in app.config.find_sections("section_")]
        return ul_form
