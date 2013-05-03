import httplib
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from tranny import datastore
webui = Blueprint('webui', __name__, template_folder="templates", static_folder="static", url_prefix="/webui")


@webui.route("/")
def index():
    newest = datastore.fetch_newest()
    try:
        return render_template("index.html", newest=newest)
    except TemplateNotFound:
        abort(httplib.NOT_FOUND)


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
