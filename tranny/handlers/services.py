# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from json import dumps
import httplib
from flask import Blueprint, abort, request
from flask.ext.login import login_required
from ..app import config, logger
from ..ui import render_template

services = Blueprint("services", __name__, url_prefix="/services")


@services.route("/")
@login_required
def index():
    btn_info = config.get_section_values("service_broadcastthenet")
    return render_template("services.html", section="services", btn=btn_info)


@services.route("/btn/save", methods=['POST'])
@login_required
def btn_save():
    try:
        token = request.values['btn_api_token']
        url = request.values['btn_url']
        interval = int(request.values['btn_interval'])
        enabled = request.values['btn_enabled']
    except (KeyError, TypeError):
        logger.warning("Malformed request received")
        abort(httplib.BAD_REQUEST)
    else:
        section = "service_broadcastthenet"
        status = 1
        msg = "There was an error saving your BTN config"
        config.set(section, "api_token", token)
        config.set(section, "enabled", enabled)
        config.set(section, "url", url)
        config.set(section, "interval", interval)
        if config.save():
            status = 0
            msg = "Saved BTN configuration successfully"
        return dumps({'msg': msg, 'status': status})
