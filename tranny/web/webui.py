import platform
import time
import sys
import httplib
from collections import OrderedDict
from json import dumps
from logging import getLogger
from flask import Blueprint, render_template, request, redirect, url_for, abort, g
from flask.ext.login import login_user, logout_user, login_required, current_user
from tranny import config, log_history, info
from tranny import datastore
from tranny.datastore import stats
from tranny.configuration import NoOptionError, NoSectionError
from tranny.web import add_user_message, render

# Use a Flask mountpoint at /webui
webui = Blueprint('webui', __name__, template_folder="templates", static_folder="static", url_prefix="/webui")
log = getLogger()


@webui.route("/", methods=['GET'])
@login_required
def index():
    newest = datastore.fetch_download(limit=25)
    return render("index.html", newest=newest, section="stats")


@webui.route("/stats/service_totals", methods=['GET'])
@login_required
def service_totals():
    return dumps(stats.service_totals(datastore.fetch_download()))


@webui.route("/stats/section_totals", methods=['GET'])
@login_required
def section_totals():
    return dumps(stats.section_totals(datastore.fetch_download()))


@webui.route("/stats/service_type_totals", methods=['GET'])
@login_required
def service_type_totals():
    return dumps(stats.service_type_totals(datastore.fetch_download()))


@webui.route("/filters/delete", methods=['POST'])
@login_required
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
    return dumps(response)


@webui.route("/filters/add", methods=['POST'])
@login_required
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
@login_required
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
@login_required
def services():
    btn_info = config.get_section_values("service_broadcastthenet")
    return render_template("services.html", section="services", btn=btn_info)


@webui.route("/services/btn/save", methods=['POST'])
@login_required
def services_btn_save():
    try:
        token = request.values['btn_api_token']
        url = request.values['btn_url']
        interval = int(request.values['btn_interval'])
        enabled = request.values['btn_enabled']
    except (KeyError, TypeError):
        log.warning("Malformed request received")
        abort(httplib.BAD_REQUEST)
    else:
        section = "service_broadcastthenet"
        status = 1
        msg = "There was an error saving your BTN config"
        try:
            config.set(section, "api_token", token)
            config.set(section, "enabled", enabled)
            config.set(section, "url", url)
            config.set(section, "interval", interval)
            if config.save():
                status = 0
                msg = "Saved BTN configuration successfully"
        except (Exception):
            pass
        finally:
            return dumps({'msg': msg, 'status': status})


@webui.route("/rss", methods=['GET'])
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
    return render("rss.html", section="rss", feeds=feed_data)


@webui.route("/rss/delete", methods=['POST'])
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


@webui.route("/rss/create", methods=['POST'])
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
        log.error(msg)
        add_user_message(msg, "success")
    else:
        log.info(msg)
        add_user_message(msg, "alert")
    return redirect(url_for(".rss"))


@webui.route("/rss/save", methods=['POST'])
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


@webui.route("/syslog")
@login_required
def syslog():
    return render("syslog.html", section="syslog", logs=log_history.get(100))


@webui.route("/system")
@login_required
def system():
    about_info = OrderedDict()
    about_info['Hostname'] = platform.node()
    about_info['Platform'] = "{0} ({1})".format(platform.platform(), platform.architecture()[0])
    about_info['Python'] = "{0} {1}".format(platform.python_implementation(), platform.python_version())
    about_info['Uptime-Sys'] = time.strftime("%H:%M:%S", time.gmtime(info.uptime_sys()))
    about_info['Uptime-App'] = time.strftime("%H:%M:%S", time.gmtime(info.uptime_app()))
    try:
        # TODO Win/OSX support
        if hasattr(sys, "real_prefix"):
            about_info['Distribution'] = "VirtualEnv"
        else:
            distro = platform.linux_distribution()
            if distro[0]:
                about_info['Distribution'] = "{0} {1} {2}".format(distro[0], distro[1], distro[2])
    except IndexError:
        pass

    # Get disk info and sort it by path
    disk_info = info.disk_free()
    sorted_disk_info = OrderedDict()
    for key in sorted(disk_info.keys()):
        sorted_disk_info[key] = disk_info[key]

    return render("system.html", section="tranny", info=about_info, disk_info=sorted_disk_info)


@webui.route("/settings")
@login_required
def settings():
    keys = ['General', 'WebUI', 'uTorrent', 'Transmission', 'IMDB', 'TheMovieDB', 'Ignore',
            'DB', 'Sqlite', 'MySQL', 'Log', 'Section_TV', 'Section_Movies', 'Proxy']
    settings_set = {k: config.get_section_values(k.lower()) for k in keys}
    bool_values = ['enabled', 'sort_seasons', 'group_name', 'fetch_proper']
    db_types = ["sqlite", "mysql", "memory"]
    select_values = ['type']
    ignore_keys = ['quality_sd', 'quality_hd', 'quality_any']
    for k, v in settings_set.items():
        for key in [i for i in v.keys() if i in ignore_keys]:
            del settings_set[k][key]
    return render(
        "settings.html",
        section="settings",
        settings=settings_set,
        bool_values=bool_values,
        select_values=select_values,
        db_types=db_types
    )


@webui.route("/settings/save", methods=['POST'])
@login_required
def settings_save():
    for name, value in request.values.items():
        section, key = name.split("__")
        if value == "on":
            value = "true"
        elif value == "off":
            value = "false"
        config.set(section, key, value)
    if config.save():
        status = 0
        msg = "Saved settings successfully"
    else:
        status = 1
        msg = "Error saving settings"
    return dumps({'msg': msg, 'status': status})


@webui.route("/login", methods=['GET'])
def login():
    return render("login.html")


@webui.route("/login/perform", methods=['POST'])
def login_perform():
    try:
        user_name = request.values['user_name']
        user_password = request.values['user_password']
    except KeyError:
        pass
    else:
        user = datastore.fetch_user(user_name=user_name)
        if not user:
            pass
        if not user.password == user_password:
            pass

        try:
            remember = request.values['remember'].lower() == "on"
        except KeyError:
            remember = False
        login_user(user, remember=remember)
    return redirect(request.args.get("next") or url_for(".index"))


@webui.route("/logout")
def logout():
    logout_user()
    return redirect(url_for(".index"))


@webui.errorhandler(404)
def four_oh_four():
    return ":("
