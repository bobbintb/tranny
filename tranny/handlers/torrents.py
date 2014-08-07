# -*- coding: utf-8 -*-
"""
Endpoints for the /torrent sections
"""
from __future__ import unicode_literals
from functools import partial
from flask import Blueprint, current_app
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
    return dict(torrents=current_app.services.client.torrent_list())
