# -*- coding: utf-8 -*-
"""
Filter settings handlers
"""

from functools import partial
from configparser import NoOptionError, NoSectionError
from flask import Blueprint, request
from flask.ext.login import login_required
from tranny.app import config
from tranny import ui
from tranny import api

section_name = "filters"
filters = Blueprint("filters", __name__, url_prefix="/filters")
renderer = partial(ui.render, section=section_name)


@filters.route("/delete", methods=['POST'])
@renderer(fmt='json')
@login_required
def delete():
    """ Delete a filter from a section over XHR

    :return: Delete status message
    :rtype: dict
    """
    title = config.normalize_title(request.values['title'])
    section = "section_{0}".format(request.values['section'])
    quality = request.values['quality']
    filters_list = config.get_filters(section, quality)
    if title in filters_list:
        filters_list.remove(title)
        config.set_filters(section, quality, filters_list)
        response = {
            'msg': "Filter deleted successfully: {0}".format(title),
            'status': api.STATUS_OK
        }
    else:
        response = {
            'msg': "Failed to delete filter: {0}".format(title),
            'status': api.STATUS_FAIL
        }
    return response


@filters.route("/add", methods=['POST'])
@renderer(fmt='json')
@login_required
def add():
    """ Add a new filter for a title to a given section

    :return: Add status message
    :rtype: dict
    """
    title = config.normalize_title(request.values['title'])
    section = "section_{0}".format(request.values['section'])
    quality = request.values['quality']
    filters_list = config.get_filters(section, quality)
    if not title in filters_list:
        filters_list.append(title)
        config.set_filters(section, quality, filters_list)
        response = {
            'msg': "Filter added successfully: {0}".format(title),
            'status': api.STATUS_OK
        }
    else:
        response = {
            'msg': "Failed to add filter: {0}".format(title),
            'status': api.STATUS_FAIL
        }
    return response


@filters.route("/")
@renderer("filters.html")
@login_required
def index():
    """ Generate a list of filters & sections and render it to the client

    :return: Section & Filter config
    :rtype: dict
    """
    section_data = []
    for section in ['tv', 'movie']:
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
    return dict(section_data=section_data)
