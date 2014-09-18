# -*- coding: utf-8 -*-
"""
/home handlers
"""
from __future__ import unicode_literals
from functools import partial
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

section_name = "home"
home = Blueprint(section_name, __name__, url_prefix="/home")
renderer = partial(ui.render, section=section_name)


@home.route("/")
@renderer("index.html")
@login_required
def index():
    """ Show the home view which is mostly a dashboard type view so we are calculating
    metrics for various areas

    TODO remove the 2nd download query once we fix not having a source_id, or at least make sure
    its not actually a problem

    :return: Mostly metric data and newest releases
    :rtype: dict
    """
    session = Session()
    downloads = session.query(Download).filter(Download.source_id > 0).all()
    provider_totals = stats.count_totals(downloads, lambda v: v.source.source_name).items()
    section_totals = stats.count_totals(downloads, lambda v: v.section.section_name).items()
    provider_type_totals = stats.provider_type_counter(downloads).items()
    newest = Session.query(Download).order_by(Download.entity_id.desc()).limit(25).all()
    return dict(
        newest=newest,
        provider_totals=provider_totals,
        section_totals=section_totals,
        provider_type_totals=provider_type_totals
    )


@home.route("/syslog")
@renderer("syslog.html")
@login_required
def syslog():
    """ This is currently a placeholder for showing application logs which we do not
    currently have a method to actually show over webui right now

    :return: Log data
    :rtype: dict
    """
    return dict(logs=[])


@home.route("/system")
@renderer("system.html")
@login_required
def system():
    """ Show system / OS info

    # TODO Better Win/OSX/BSD? support.

    :return: System info
    :rtype: dict
    """
    about_info = OrderedDict()
    about_info['Hostname'] = platform.node()
    about_info['Platform'] = "{0} ({1})".format(platform.platform(), platform.architecture()[0])
    about_info['Python'] = "{0} {1}".format(platform.python_implementation(), platform.python_version())
    about_info['Uptime-Sys'] = time.strftime("%H:%M:%S", time.gmtime(util.uptime_sys()))
    about_info['Uptime-App'] = time.strftime("%H:%M:%S", time.gmtime(util.uptime_app()))
    try:
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

    # Get arbitary client information
    client_info = client.get().client_information()

    return dict(info=about_info, disk_info=sorted_disk_info, client_info=client_info)
