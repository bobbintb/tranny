# -*- coding: utf-8 -*-
"""
RSS Configuration routes
"""
from __future__ import unicode_literals
from ConfigParser import NoOptionError
from functools import partial
import logging
from flask import Blueprint, request, redirect, url_for
from flask.ext.login import login_required
from tranny.app import config
from tranny import ui
from tranny import api

section_name = "rss"
rss = Blueprint(section_name, __name__, url_prefix="/rss")
renderer = partial(ui.render, section=section_name)
log = logging.getLogger("web.rss")


@rss.route("/", methods=['GET'])
@renderer("rss.html")
@login_required
def index():
    """ Generate feed configuration data from the local config and show
    it to the user to allow editing

    :return: RSS Configuration
    :rtype: dict
    """
    feed_data = {}
    for section in config.find_sections("rss_"):
        settings = config.get_section_values(section)
        # for key, default, type_func in option_set:
        #     settings[key] = config.get_default(section, key, default, type_func)
        if not "enabled" in settings:
            try:
                enabled = config.getboolean(section, "enabled")
            except NoOptionError:
                enabled = False
            settings['enabled'] = "0" if enabled else "1"
        tpl_key = section.split("_")[1]
        feed_data[tpl_key] = settings
    return dict(feeds=feed_data)


@rss.route("/delete", methods=['POST'])
@renderer(fmt="json")
@login_required
def delete():
    """ Delete a RSS feed from the config over XHR

    :return: Deletion status response
    :rtype: dict
    """
    status = api.STATUS_FAIL
    try:
        feed = "rss_{0}".format(request.values['feed'])
        if not config.has_section(feed):
            raise KeyError()
    except KeyError:
        msg = "Invalid feed name"
    else:
        if config.remove_section(feed) and config.save():
            msg = "RSS Feed deleted successfully: {0}".format(request.values['feed'])
            status = api.STATUS_OK
        else:
            msg = "Failed to remove configuration section: {0}".format(feed)
    response = {
        'msg': msg,
        'status': status
    }
    return response


@rss.route("/create", methods=['POST'])
@renderer()
@login_required
def create():
    """ Create a new RSS feed over XHR

    :return: Feed creation status response
    :rtype: Response
    """
    status = api.STATUS_FAIL
    try:
        feed = "rss_{0}".format(request.values['new_short_name'])
        if config.has_section(feed):
            raise KeyError()
        else:
            config.add_section(feed)
    except KeyError:
        msg = "Duplicate feed name"
    else:
        try:
            config.set(feed, "url", request.values['new_url'])
            config.set(feed, "interval", request.values['new_interval'])
            config.set(feed, "enabled", request.values['new_enabled'])
            if config.save():
                msg = "RSS Feed saved successfully: {0}".format(request.values['new_short_name'])
                status = api.STATUS_OK
            else:
                msg = "Error saving config to disk."
        except KeyError:
            msg = "Failed to save config. Malformed request: {0}".format(feed)
    log.error(msg) if status == api.STATUS_FAIL else log.info(msg)
    return redirect(url_for(".index"))


@rss.route("/save", methods=['POST'])
@renderer(fmt='json')
@login_required
def save():
    """ Save the new config values of an existing feed over XHR

    :return: Save status response
    :rtype: dict
    """
    status = api.STATUS_FAIL
    try:
        feed = "rss_{0}".format(request.values['feed'])
        if not config.has_section(feed):
            raise KeyError()
    except KeyError:
        msg = "Invalid feed name"
    else:
        try:
            config.set(feed, "url", request.values['url'])
            config.set(feed, "interval", request.values['interval'])
            config.set(feed, "enabled", request.values['enabled'])
            msg = "RSS Feed saved successfully: {0}".format(request.values['feed'])
            status = api.STATUS_OK
        except KeyError:
            msg = "Failed to save config. Malformed request: {0}".format(feed)
    return dict(msg=msg, status=status)
