# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from json import dumps
from flask import Blueprint, current_app
from flask.ext.login import login_required
from tranny import stats as stat, models

stats = Blueprint("stats", __name__, url_prefix="/stats")


@stats.route("/service_totals")
@login_required
def svc_totals():
    data_set = stat.service_totals(models.DownloadEntity.query.all())
    return dumps(data_set)


@stats.route("/section_totals")
@login_required
def sec_totals():
    data_set = stat.section_totals(models.DownloadEntity.query.all())
    return dumps(data_set)


@stats.route("/service_type_totals")
@login_required
def type_totals():
    data_set = stat.service_type_totals(models.DownloadEntity.query.all())
    return dumps(data_set)
