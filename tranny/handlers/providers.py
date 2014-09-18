# -*- coding: utf-8 -*-
"""
/service route handlers
"""
from __future__ import unicode_literals
from functools import partial

try:
    import http.client as httplib
except ImportError:
    import httplib
import logging
from flask import Blueprint, abort, request, flash, redirect, url_for
from flask.ext.login import login_required
from tranny.app import config
from tranny import ui

section_name = 'providers'
providers = Blueprint(section_name, __name__, url_prefix="/providers")
renderer = partial(ui.render, section=section_name)

log = logging.getLogger("web.providers")


@providers.route("/")
@renderer("providers.html")
@login_required
def index():
    """ Generate and render a list of provider configs

    :return: Provider configs
    :rtype: dict
    """
    provider_info = {k: config.get_section_values(k) for k in config.find_sections("provider_")}
    return dict(provider_info=provider_info)


@providers.route("/save/<provider>", methods=['POST'])
@login_required
def save(provider):
    """ Save a providers configuration

    TODO Use PUT?

    :param provider: Provider key/name
    :type provider: unicode
    :return: Redirect response
    :rtype: Response
    """
    try:
        for k, v in request.values.items():
            config.set(provider, k.replace(provider + "_", ""), v)
    except (KeyError, TypeError):
        log.warning("Malformed request received")
        abort(httplib.BAD_REQUEST)
    else:
        if config.save():
            flash("Saved configuration successfully")
        else:
            flash("There was an error saving your provider config")
        return redirect(url_for(".index"))
