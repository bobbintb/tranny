# -*- coding: utf-8 -*-

from os.path import join, dirname
from flask.ext.wtf import Form
from tranny import constants
from wtforms import HiddenField, SelectField, validators
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask.ext import uploads

torrent_file_set = uploads.UploadSet(
    'torrent',
    extensions=['torrent'],
    default_dest=lambda p: join(dirname(__file__), 'uploads')
)


class UploadForm(Form):
    torrent_file = FileField("Torrent File", validators=[FileRequired(), FileAllowed(torrent_file_set)])
    section = SelectField(
        "Section",
        validators=[validators.required()],
        choices=[
            ["section_{}".format(constants.MEDIA_TV), "TV"],
            ["section_{}".format(constants.MEDIA_MOVIE), "Movie"]
        ]
    )
    next_url = HiddenField("Next URL", default="")
