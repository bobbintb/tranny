from flask.ext.wtf import Form
from wtforms import FileField, validators, SubmitField


class UploadForm(Form):
    torrent_file = FileField("Torrent File", [validators.regexp(r"^[^/\\]\.jpg$")])
    submit = SubmitField("Upload")
