from flask.ext.wtf import Form
from wtforms import HiddenField
from flask_wtf.file import FileField, FileAllowed, FileRequired


class UploadForm(Form):
    torrent_file = FileField("Torrent File", validators=[])
    next_url = HiddenField("Next URL", default="")

