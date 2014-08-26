# -*- coding: utf-8 -*-
"""
Basic endpoints for the /torrent sections and the websocket api
"""
from __future__ import unicode_literals
from functools import partial
from flask import Blueprint
from flask.ext.socketio import emit
from tranny import ui, api, client

section_name = 'torrents'
renderer = partial(ui.render, section=section_name)
torrents = Blueprint(section_name, __name__, url_prefix="/torrents")


@torrents.route("/")
@renderer("torrents.html")
def index():
    return dict()


@api.on(api.EVENT_TORRENT_RECHECK)
def handle_recheck(message):
    info_hash = message.get('info_hash', [])
    resp = client.get().torrent_recheck(info_hash)
    api.emit(api.EVENT_TORRENT_RECHECK_RESPONSE, resp)
    api.flash("Rechecking..!")


@api.on(api.EVENT_TORRENT_ANNOUNCE)
def handle_announce(message):
    """ (re)announce the torrent(s) to the tracker

    :param message:
    :type message: dict
    :return:
    :rtype:
    """
    info_hash = message.get('data', [])
    if client.get().torrent_reannounce(info_hash):
        status = api.STATUS_OK
    else:
        status = api.STATUS_FAIL
    api.emit(api.EVENT_TORRENT_ANNOUNCE_RESPONSE, status=status)


@api.on(api.EVENT_TORRENT_LIST)
def handle_list_all():
    """ Return a list of all torrents currently being tracked """
    torrent_list = client.get().torrent_list()
    api.emit(api.EVENT_TORRENT_LIST_RESPONSE, data=torrent_list)


@api.on(api.EVENT_TORRENT_STOP)
def handle_stop(message):
    info_hash = message.get('info_hash', [])
    client.get().torrent_stop(info_hash)
    api.emit(api.EVENT_TORRENT_SPEED_RESPONSE, dict(info_hash=info_hash))
    api.flash("Stopped successfully")


@api.on(api.EVENT_TORRENT_START)
def handle_start(message):
    info_hash = message.get('info_hash', [])
    client.get().torrent_start(info_hash)
    api.emit(api.EVENT_TORRENT_START_RESPONSE, dict(info_hash=info_hash))
    api.flash("Started successfully")


@api.on(api.EVENT_TORRENT_DETAILS)
def handle_details(message):
    info_hash = message.get('info_hash', None)
    data = dict()
    if info_hash:
        data = client.get().torrent_status(info_hash)
        status = api.STATUS_OK
    else:
        status = api.STATUS_INCOMPLETE_REQUEST
    api.emit(api.EVENT_TORRENT_DETAILS_RESPONSE, data=data, status=status)


@api.on(api.EVENT_TORRENT_SPEED)
def handle_speed(message):
    info_hash = message.get('info_hash', None)
    if info_hash:
        tor_speed = client.get().torrent_speed(info_hash)
        api.emit(api.EVENT_TORRENT_SPEED_RESPONSE, data=tor_speed)
    else:
        api.emit(api.EVENT_TORRENT_SPEED_RESPONSE, status=api.STATUS_FAIL)


@api.on(api.EVENT_SPEED_OVERALL)
def handle_speed_overall(message=None):
    up, dn = client.get().current_speeds()
    emit(api.EVENT_SPEED_OVERALL_RESPONSE, dict(data=dict(up=up, dn=dn)))


@api.on(api.EVENT_TORRENT_FILES)
def handle_files(message):
    info_hash = message.get('info_hash', None)
    tor_files = client.get().torrent_files(info_hash)
    emit(api.EVENT_TORRENT_FILES_RESPONSE, dict(status=api.STATUS_OK, data=tor_files))


@api.on(api.EVENT_TORRENT_PEERS)
def handle_peers(message):
    info_hash = message.get('info_hash', None)
    data = client.get().torrent_peers(info_hash)
    emit(api.EVENT_TORRENT_PEERS_RESPONSE, dict(status=api.STATUS_OK, data=data))


@api.on(api.EVENT_TORRENT_REMOVE)
def handle_remove(message):
    info_hash = message.get('info_hash', None)
    remove_data = message.get('remove_data', False)
    torrent = client.get().torrent_status(info_hash)
    if not torrent:
        status = api.STATUS_INVALID_INFO_HASH
    else:
        if client.get().torrent_remove(info_hash, remove_data=remove_data):
            status = api.STATUS_OK
        else:
            status = api.STATUS_FAIL
    emit(api.EVENT_TORRENT_REMOVE_RESPONSE, dict(status=status, info_hash=info_hash))
