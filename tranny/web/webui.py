import httplib
from json import dumps
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from tranny import db
from tranny.datastore import stats


webui = Blueprint('webui', __name__, template_folder="templates", static_folder="static", url_prefix="/webui")


@webui.route("/")
def index():
    try:
        return render_template("index.html", newest=db.fetch(limit=25))
    except TemplateNotFound:
        abort(httplib.NOT_FOUND)


@webui.route("/stats/source_leaders")
def source_leaders():
    return dumps(stats.service_totals(db.fetch(limit=False)))


@webui.route("/stats/section_totals")
def section_totals():
    return dumps(stats.section_totals(db.fetch(limit=False)))


@webui.route("/filters")
def filters():
    try:
        return render_template("filters.html")
    except TemplateNotFound:
        abort(httplib.NOT_FOUND)


@webui.route("/services")
def services():
    try:
        return render_template("services.html")
    except TemplateNotFound:
        abort(httplib.NOT_FOUND)


@webui.route("/settings")
def settings():
    try:
        return render_template("settings.html")
    except TemplateNotFound:
        abort(httplib.NOT_FOUND)
