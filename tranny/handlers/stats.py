from json import dumps
from flask import Blueprint
from flask.ext.login import login_required

stats = Blueprint("stats", __name__, url_prefix="/stats")


@stats.route("/service_totals")
@login_required
def service_totals():
    return dumps(stats.service_totals(datastore.fetch_download()))


@stats.route("/section_totals")
@login_required
def section_totals():
    return dumps(stats.section_totals(datastore.fetch_download()))


@stats.route("/service_type_totals")
@login_required
def type_totals():
    return dumps(stats.service_type_totals(datastore.fetch_download()))
