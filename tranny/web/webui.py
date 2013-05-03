import httplib
from flask import Blueprint, render_template, abort, url_for
from jinja2 import TemplateNotFound

webui = Blueprint('webui', __name__, template_folder="templates", static_folder="static", url_prefix="/webui")

print(webui.has_static_folder)


@webui.route("/")
def index():
    try:
        return render_template("base.html")
    except TemplateNotFound:
        abort(httplib.NOT_FOUND)
