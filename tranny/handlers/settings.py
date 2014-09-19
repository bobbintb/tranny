# -*- coding: utf-8 -*-
"""
Settings routes for settings outside of providers/services/filters
"""
from __future__ import unicode_literals
from functools import partial
import logging
from json import dumps
from flask import request, Blueprint
from flask.ext.login import login_required
from tranny.app import config
from tranny import ui
from tranny import api

section_name = "settings"
settings = Blueprint(section_name, __name__, url_prefix="/settings")
renderer = partial(ui.render, section=section_name)

@settings.route("/")
@renderer("settings.html")
@login_required
def index():
    """ Generate config data for all the sections in the config

    :return: Config data
    :rtype: dict
    """
    groups = { 'General': [ 'General',
                            'WebUI',
                            'Ignore',
                            'Log',
                            'Proxy'],
               'Clients': [ 'client_uTorrent',
                            'client_Transmission',
                            'client_rTorrent',
                            'client_Deluge'],
               'Services': [ 'service_IMDB',
                             'service_TheMovieDB'],
               'Sections': [ 'section_TV',
                             'section_Movies']
             }
    settings_data = {}
    for group, sections in groups.iteritems():
        settings_data[group] = {}
        for s in sections:
            settings_data[group][s] = config.get_section_values(s.lower())
    #settings_set = {k: config.get_section_values(k.lower()) for k in keys}
    bool_values = ['enabled', 'sort_seasons', 'group_name', 'fetch_proper']
    select_values = ['type']
    ignore_keys = ['quality_sd', 'quality_hd', 'quality_any']
    #for k, v in settings_set.items():
    #    for key in [i for i in v.keys() if i in ignore_keys]:
    #        del settings_set[k][key]
    return dict(
        settings=settings_data,
        bool_values=bool_values,
        select_values=select_values
    )


@settings.route("/save", methods=['POST'])
@renderer(fmt="json")
@login_required
def save():
    """ Save the settings for the posted config section

    :return: Save status response
    :rtype: dict
    """
    for name, value in request.values.items():
        section, key = name.split("__")
        if value == "on":
            value = "true"
        elif value == "off":
            value = "false"
        config.set(section, key, value)
    if config.save():
        status = api.STATUS_OK
        msg = "Saved settings successfully"
    else:
        status = api.STATUS_FAIL
        msg = "Error saving settings"
    return dumps({'msg': msg, 'status': status})
