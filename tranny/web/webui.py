import httplib
from json import dumps
from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound
from tranny import db, config, log_history
from tranny.datastore import stats
from tranny.configuration import NoOptionError, NoSectionError

webui = Blueprint('webui', __name__, template_folder="templates", static_folder="static", url_prefix="/webui")


@webui.route("/", methods=['GET'])
def index():
    return render_template("index.html", newest=db.fetch(limit=25), section="stats")


@webui.route("/stats/service_totals", methods=['GET'])
def service_totals():
    return dumps(stats.service_totals(db.fetch(limit=False)))


@webui.route("/stats/section_totals", methods=['GET'])
def section_totals():
    return dumps(stats.section_totals(db.fetch(limit=False)))


@webui.route("/stats/service_type_totals", methods=['GET'])
def service_type_totals():
    return dumps(stats.service_type_totals(db.fetch(limit=False)))


@webui.route("/filters/delete", methods=['POST'])
def filters_delete():
    title = config.normalize_title(request.values['title'])
    section = "section_{0}".format(request.values['section'])
    quality = request.values['quality']
    filters_list = config.get_filters(section, quality)
    if title in filters_list:
        filters_list.remove(title)
        config.set_filters(section, quality, filters_list)
        response = {
            'msg': "Filter deleted successfully: {0}".format(title),
            'status': 0
        }
    else:
        response = {
            'msg': "Failed to delete filter: {0}".format(title),
            'status': 1
        }
    resp = dumps(response)
    return resp


@webui.route("/filters/add", methods=['POST'])
def filters_add():
    title = config.normalize_title(request.values['title'])
    section = "section_{0}".format(request.values['section'])
    quality = request.values['quality']
    filters_list = config.get_filters(section, quality)
    if not title in filters_list:
        filters_list.append(title)
        config.set_filters(section, quality, filters_list)
        response = {
            'msg': "Filter added successfully: {0}".format(title),
            'status': 0
        }
    else:
        response = {
            'msg': "Failed to add filter: {0}".format(title),
            'status': 1
        }
    resp = dumps(response)
    return resp


@webui.route("/filters", methods=['GET'])
def filters():
    section_data = []
    for section in ['tv', 'movies']:
        config_section = "section_{0}".format(section)
        section_info = {}
        for key in ['dl_path', 'group_name', 'sort_seasons']:
            try:
                section_info[key] = config.get(config_section, key)
            except (NoOptionError, NoSectionError):
                pass
        for key in ['quality_hd', 'quality_sd', 'quality_any']:
            try:
                values = [" ".join(show.split()) for show in config.get(config_section, key).split(",") if show]
                if values:
                    section_info[key] = values

            except (NoOptionError, NoSectionError):
                pass
        section_info['section'] = section
        section_data.append(section_info)
    return render_template("filters.html", section_data=section_data, section="filters")


@webui.route("/services")
def services():
    return render_template("services.html", section="services")


@webui.route("/rss")
def rss():
    return render_template("rss.html", section="rss")


@webui.route("/syslog")
def syslog():
    return render_template("syslog.html", section="syslog", logs=log_history.get(100))


@webui.route("/settings")
def settings():
    return render_template("settings.html", section="settings")
