# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from json import dumps
from flask import Blueprint
from flask.ext.login import login_required
from ..stats import service_totals, section_totals, service_type_totals
from tranny.models import DownloadEntity

stats = Blueprint("stats", __name__, url_prefix="/stats")


@stats.route("/service_totals")
@login_required
def svc_totals():
    data_set = service_totals(DownloadEntity.query.all())
    return dumps(data_set)


@stats.route("/section_totals")
@login_required
def sec_totals():
    data_set =  section_totals(DownloadEntity.query.all())
    return dumps(data_set)


@stats.route("/service_type_totals")
@login_required
def type_totals():
    data_set = service_type_totals(DownloadEntity.query.all())
    return dumps(data_set)
