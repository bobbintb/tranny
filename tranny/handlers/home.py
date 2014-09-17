# -*- coding: utf-8 -*-
"""
/home handlers
"""
from __future__ import unicode_literals
import platform
import time
import sys
from collections import OrderedDict
from flask import Blueprint
from flask.ext.login import login_required
from tranny import ui
from tranny import util
from tranny import stats
from tranny.app import Session
from tranny.models import Download

home = Blueprint("home", __name__, url_prefix="/home")


@home.route("/")
@login_required
def index():
    session = Session()
    downloads = session.query(Download).filter(Download.source_id > 0).all()
    provider_totals = stats.count_totals(downloads, lambda v: v.source.source_name).items()
    section_totals = stats.count_totals(downloads, lambda v: v.section.section_name).items()
    provider_type_totals = stats.provider_type_counter(downloads).items()
    newest = Session.query(Download).order_by(Download.entity_id.desc()).limit(25).all()
    return ui.render_template(
        "index.html", newest=newest, section="stats",
        provider_totals=provider_totals,
        section_totals=section_totals,
        provider_type_totals=provider_type_totals
    )


@home.route("/syslog")
@login_required
def syslog():
    return ui.render_template("syslog.html", section="syslog", logs=[])


@home.route("/system")
@login_required
def system():
    about_info = OrderedDict()
    about_info['Hostname'] = platform.node()
    about_info['Platform'] = "{0} ({1})".format(platform.platform(), platform.architecture()[0])
    about_info['Python'] = "{0} {1}".format(platform.python_implementation(), platform.python_version())
    about_info['Uptime-Sys'] = time.strftime("%H:%M:%S", time.gmtime(util.uptime_sys()))
    about_info['Uptime-App'] = time.strftime("%H:%M:%S", time.gmtime(util.uptime_app()))
    try:
        # TODO Win/OSX support
        if hasattr(sys, "real_prefix"):
            about_info['Distribution'] = "VirtualEnv"
        else:
            distro = platform.linux_distribution()
            if distro[0]:
                about_info['Distribution'] = "{0} {1} {2}".format(distro[0], distro[1], distro[2])
    except IndexError:
        pass

    # Get disk info and sort it by path
    disk_info = util.disk_free()
    sorted_disk_info = OrderedDict()
    for key in sorted(disk_info.keys()):
        sorted_disk_info[key] = disk_info[key]

    return ui.render_template("system.html", section="tranny", info=about_info, disk_info=sorted_disk_info)
