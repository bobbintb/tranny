from ConfigParser import NoOptionError
from json import dumps
from flask import Blueprint, request, redirect, url_for, current_app
from flask.ext.login import login_required
from .. import config
from ..ui import render_template

rss = Blueprint("rss", __name__, url_prefix="/rss")


@rss.route("/", methods=['GET'])
@login_required
def rss():
    feed_data = {}
    for section in config.find_sections("rss_"):
        settings = config.get_section_values(section)
        # for key, default, type_func in option_set:
        #     settings[key] = config.get_default(section, key, default, type_func)
        if not "enabled" in settings:
            try:
                enabled = config.getboolean(section, "enabled")
            except NoOptionError:
                enabled = False
            settings['enabled'] = "0" if enabled else "1"
        tpl_key = section.split("_")[1]
        feed_data[tpl_key] = settings
    return render_template("rss.html", section="rss", feeds=feed_data)


@rss.route("/delete", methods=['POST'])
@login_required
def rss_delete():
    status = 1
    try:
        feed = "rss_{0}".format(request.values['feed'])
        if not config.has_section(feed):
            raise KeyError()
    except KeyError:
        msg = "Invalid feed name"
    else:

        if config.remove_section(feed) and config.save():
            msg = "RSS Feed deleted successfully: {0}".format(request.values['feed'])
            status = 0
        else:
            msg = "Failed to remove configuration section: {0}".format(feed)
    response = {
        'msg': msg,
        'status': status
    }
    return dumps(response)


@rss.route("/create", methods=['POST'])
@login_required
def rss_create():
    status = 1
    try:
        feed = "rss_{0}".format(request.values['new_short_name'])
        if config.has_section(feed):
            raise KeyError()
        else:
            config.add_section(feed)
    except KeyError:
        msg = "Duplicate feed name"
    else:
        try:
            config.set(feed, "url", request.values['new_url'])
            config.set(feed, "interval", request.values['new_interval'])
            config.set(feed, "enabled", request.values['new_enabled'])

            if config.save():
                msg = "RSS Feed saved successfully: {0}".format(request.values['new_short_name'])
                status = 0
            else:
                msg = "Error saving config to disk."
        except KeyError:
            msg = "Failed to save config. Malformed request: {0}".format(feed)
    if status == 1:
        current_app.logger.error(msg)
    else:
        current_app.logger.info(msg)
    return redirect(url_for(".index"))


@rss.route("/rss/save", methods=['POST'])
@login_required
def rss_save():
    status = 1
    try:
        feed = "rss_{0}".format(request.values['feed'])
        if not config.has_section(feed):
            raise KeyError()
    except KeyError:
        msg = "Invalid feed name"
    else:
        try:
            config.set(feed, "url", request.values['url'])
            config.set(feed, "interval", request.values['interval'])
            config.set(feed, "enabled", request.values['enabled'])
            msg = "RSS Feed saved successfully: {0}".format(request.values['feed'])
            status = 0
        except KeyError:
            msg = "Failed to save config. Malformed request: {0}".format(feed)
    return dumps({'msg': msg, 'status': status})
