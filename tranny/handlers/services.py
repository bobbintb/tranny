# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import httplib
from flask import Blueprint, abort, request, flash, redirect, url_for
from flask.ext.login import login_required
from tranny.app import config, logger
from tranny import ui

services = Blueprint("services", __name__, url_prefix="/services")


@services.route("/")
@login_required
def index():
    service_info = {k: config.get_section_values(k) for k in config.find_sections("service_")}
    return ui.render_template("services.html", section="services", service_info=service_info)


@services.route("/save/<service>", methods=['POST'])
@login_required
def save(service):
    try:
        for k, v in request.values.items():
            config.set(service, k.replace(service + "_", ""), v)
    except (KeyError, TypeError):
        logger.warning("Malformed request received")
        abort(httplib.BAD_REQUEST)
    else:
        if config.save():
            flash("Saved configuration successfully")
        else:
            flash("There was an error saving your config")
        return redirect(url_for(".index"))
