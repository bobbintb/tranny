# -*- coding: utf-8 -*-
"""
Endpoints for the /torrent sections
"""
from __future__ import unicode_literals
from functools import partial
from flask import Blueprint, current_app, request
from tranny import ui

section_name = 'torrents'
renderer = partial(ui.render, section=section_name)
torrents = Blueprint(section_name, __name__, url_prefix="/torrents")


@torrents.route("/")
@renderer("torrents.html")
def index():
    return dict()


@torrents.route("/list")
@renderer(fmt='json')
def list():
    data = current_app.services.client.torrent_list()
    return dict(data=data)


@torrents.route('/stop', methods=['POST'])
@renderer(fmt='json')
def stop():
    current_app.services.client.torrent_stop(request.json)
    return dict(status=0)


@torrents.route('/start', methods=['POST'])
@renderer(fmt='json')
def start():
    current_app.services.client.torrent_start(request.json)
    return dict(status=0)
