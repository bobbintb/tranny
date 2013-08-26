# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import platform
import time
import sys
from collections import OrderedDict
from flask import Blueprint
from flask.ext.login import login_required
from ..ui import render_template
from ..models import DownloadEntity
from ..util import uptime_app, uptime_sys, disk_free


home = Blueprint("home", __name__, url_prefix="/home")


@home.route("/")
@login_required
def index():
    newest = DownloadEntity.query.limit(25).all()
    return render_template("index.html", newest=newest, section="stats")


@home.route("/syslog")
@login_required
def syslog():
    return render_template("syslog.html", section="syslog", logs=[])


@home.route("/system")
@login_required
def system():
    about_info = OrderedDict()
    about_info['Hostname'] = platform.node()
    about_info['Platform'] = "{0} ({1})".format(platform.platform(), platform.architecture()[0])
    about_info['Python'] = "{0} {1}".format(platform.python_implementation(), platform.python_version())
    about_info['Uptime-Sys'] = time.strftime("%H:%M:%S", time.gmtime(uptime_sys()))
    about_info['Uptime-App'] = time.strftime("%H:%M:%S", time.gmtime(uptime_app()))
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
    disk_info = disk_free()
    sorted_disk_info = OrderedDict()
    for key in sorted(disk_info.keys()):
        sorted_disk_info[key] = disk_info[key]

    return render_template("system.html", section="tranny", info=about_info, disk_info=sorted_disk_info)
