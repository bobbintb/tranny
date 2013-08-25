from json import dumps
from ConfigParser import NoOptionError, NoSectionError
from flask import Blueprint, request
from flask.ext.login import login_required
from ..app import config
from ..ui import render_template

filters = Blueprint("filters", __name__, url_prefix="/filters")


@filters.route("/delete", methods=['POST'])
@login_required
def delete():
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
    return dumps(response)


@filters.route("/add", methods=['POST'])
@login_required
def add():
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


@filters.route("/")
@login_required
def index():
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
