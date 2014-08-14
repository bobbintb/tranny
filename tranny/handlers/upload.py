# -*- coding: utf-8 -*-
from flask import Blueprint, request, flash, url_for, redirect

from tranny import exceptions, app, torrent, release, forms

upload = Blueprint("upload", __name__, url_prefix='/upload')


class HTTPUpload(object):
    name = "http_upload"


@upload.route("/", methods=['POST'])
def handler():
    form = forms.UploadForm.make()
    if form.validate_on_submit():
        file_data = request.files['torrent_file'].stream.read()
        try:
            torrent_struct = torrent.Torrent.from_str(file_data)

            tor_data = release.TorrentData(torrent_struct.name, file_data, form.section.data)
            if app.services.add(tor_data, HTTPUpload()):
                flash("Torrent {} uploaded successfully".format(torrent_struct.name), "success")
            else:
                flash("Failed to upload torrent", "alert")
        except exceptions.TrannyException as err:
            flash(err.message, "alert")
    elif form.errors:
        for field, error in form.errors.items():
            try:
                flash("[{}] {}".format(field, ' && '.join(error)), "alert")
            except:
                pass
    try:
        next_url = request.form['next_url']
    except KeyError:
        next_url = url_for("home.index")
    return redirect(next_url)
