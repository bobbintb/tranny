from json import dumps
from logging import getLogger
from flask import Blueprint, render_template, request, redirect, url_for, session
from tranny import db, config, log_history
from tranny.datastore import stats
from tranny.configuration import NoOptionError, NoSectionError
from tranny.web import add_user_message, render

webui = Blueprint('webui', __name__, template_folder="templates", static_folder="static", url_prefix="/webui")
log = getLogger("web")


@webui.route("/", methods=['GET'])
def index():
    return render("index.html", newest=db.fetch(limit=25), section="stats")


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
    return render("filters.html", section_data=section_data, section="filters")


@webui.route("/services")
def services():
    return render_template("services.html", section="services")


@webui.route("/rss", methods=['GET'])
def rss():
    feed_data = {}
    option_set = [
        ["interval", 300, int],
        ["url", "", str]
    ]
    for section in config.find_sections("rss_"):
        settings = {}
        for key, default, type_func in option_set:
            settings[key] = config.get_default(section, key, default, type_func)
        try:
            enabled = config.getboolean(section, "enabled")
        except NoOptionError:
            enabled = False
        settings['enabled'] = "0" if enabled else "1"
        tpl_key = section.split("_")[1]
        feed_data[tpl_key] = settings
    return render("rss.html", section="rss", feeds=feed_data)


@webui.route("/rss/delete", methods=['POST'])
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


@webui.route("/rss/create", methods=['POST'])
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
        log.error(msg)
        add_user_message(msg, "success")
    else:
        log.info(msg)
        add_user_message(msg, "alert")
    return redirect(url_for(".rss"))


@webui.route("/rss/save", methods=['POST'])
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
    response = {
        'msg': msg,
        'status': status
    }
    return dumps(response)


@webui.route("/syslog")
def syslog():
    return render("syslog.html", section="syslog", logs=log_history.get(100))


@webui.route("/settings")
def settings():
    return render("settings.html", section="settings")