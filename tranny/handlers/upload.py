# -*- coding: utf-8 -*-
"""
Upload handler
"""
from flask import Blueprint, request, flash, url_for, redirect
from tranny import exceptions
from tranny import torrent
from tranny import release
from tranny import forms
from tranny.app import Session
from tranny.manager import ServiceManager
from tranny.provider.web import WebProvider

section_name = "upload"
upload = Blueprint("upload", __name__, url_prefix='/upload')


@upload.route("/", methods=['POST'])
def handler():
    """ Called when a user used the popup modal to upload a torrent manually

    :return: Redirect response
    :rtype: Response
    """
    form = forms.UploadForm()
    if form.validate_on_submit():
        file_data = request.files['torrent_file'].stream.read()
        file_name = request.files['torrent_file'].filename
        if file_name.endswith(".torrent"):
            file_name = file_name[0:len(file_name)-8]

        try:
            torrent_struct = torrent.Torrent.from_str(file_data)
            tor_data = release.TorrentData(torrent_struct.name, file_data, form.section.data)
            if ServiceManager.add(Session(), tor_data, WebProvider()):
                flash("Torrent {} uploaded successfully".format(torrent_struct.name), "success")
            else:
                flash("Failed to upload torrent", "alert")
        except exceptions.TrannyException as err:
            flash(err.message, "alert")
    elif form.errors:
        for field, error in list(form.errors.items()):
            try:
                flash("[{}] {}".format(field, ' && '.join(error)), "alert")
            except:
                pass
    try:
        next_url = request.form['next_url']
    except KeyError:
        next_url = url_for("home.index")
    return redirect(next_url)
