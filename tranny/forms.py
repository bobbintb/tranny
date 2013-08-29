# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import HiddenField, SelectField, validators
from flask_wtf.file import FileField, FileAllowed, FileRequired
from .app import torrent_file_set, config


class UploadForm(Form):
    torrent_file = FileField("Torrent File", validators=[FileRequired(), FileAllowed(torrent_file_set)])
    section = SelectField("Section", validators=[validators.required()])
    next_url = HiddenField("Next URL", default="")

    @classmethod
    def make(cls):
        ul_form = cls()
        ul_form.section.choices = [[s[len("section_"):], s[len("section_"):]]
                                   for s in config.find_sections("section_")]
        return ul_form
