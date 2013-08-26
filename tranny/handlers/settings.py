# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from json import dumps
from flask import request, Blueprint
from flask.ext.login import login_required
from ..app import config
from ..ui import render_template

settings = Blueprint("settings", __name__, url_prefix="/settings")


@settings.route("/")
@login_required
def index():
    keys = [
        'General',
        'WebUI',
        'uTorrent',
        'Transmission',
        'IMDB',
        'TheMovieDB',
        'Ignore',
        'Log',
        'Section_TV',
        'Section_Movies',
        'Proxy'
    ]
    settings_set = {k: config.get_section_values(k.lower()) for k in keys}
    bool_values = ['enabled', 'sort_seasons', 'group_name', 'fetch_proper']
    select_values = ['type']
    ignore_keys = ['quality_sd', 'quality_hd', 'quality_any']
    for k, v in settings_set.items():
        for key in [i for i in v.keys() if i in ignore_keys]:
            del settings_set[k][key]
    return render_template(
        "settings.html",
        section="settings",
        settings=settings_set,
        bool_values=bool_values,
        select_values=select_values
    )


@settings.route("/save", methods=['POST'])
@login_required
def save():
    for name, value in request.values.items():
        section, key = name.split("__")
        if value == "on":
            value = "true"
        elif value == "off":
            value = "false"
        config.set(section, key, value)
    if config.save():
        status = 0
        msg = "Saved settings successfully"
    else:
        status = 1
        msg = "Error saving settings"
    return dumps({'msg': msg, 'status': status})
