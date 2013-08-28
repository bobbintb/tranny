from flask import Blueprint, request, flash, url_for, redirect

from ..exceptions import TrannyException
from ..torrent import Torrent
from ..release import TorrentData
from ..forms import UploadForm
from ..app import service_manager

upload = Blueprint("upload", __name__, url_prefix='/upload')


class HTTPUpload(object):
    name = "http_upload"


@upload.route("/", methods=['POST'])
def index():
    form = UploadForm()
    if form.validate_on_submit():
        file_data = request.files['torrent_file'].stream.read()
        try:
            torrent_struct = Torrent.from_str(file_data)

            tor_data = TorrentData(torrent_struct.name, file_data, 'misc')
            if service_manager.add(tor_data, HTTPUpload()):
                flash("Torrent {} uploaded successfully".format(torrent_struct.name), "success")
            else:
                flash("Failed to upload torrent", "alert")
        except TrannyException as err:
            flash(err.message, "alert")
    elif form.torrent_file.errors:
        for error in form.errors:
            try:
                flash(unicode(error), "alert")
            except:
                pass
    try:
        next_url = request.form['next_url']
    except KeyError:
        next_url = url_for("home.index")
    return redirect(next_url)
