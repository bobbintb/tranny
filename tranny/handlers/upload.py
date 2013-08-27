from flask import Blueprint, request, flash
from ..forms import UploadForm

upload = Blueprint("upload", __name__, url_prefix='/upload')


@upload.route("/", methods=['GET', 'POST'])
def index():
    form = UploadForm(request.form)
    if form.validate_on_submit():
        pass
    elif form.torrent_file.errors:
        for error in form.torrent_file.errors:
            flash(error, "alert")
