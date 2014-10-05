# -*- coding: utf-8 -*-
"""
Basic endpoints for the /torrent sections and the websocket api
"""
from __future__ import unicode_literals
from functools import partial
import logging
from flask import Blueprint
from tranny import ui
from tranny import api
from tranny import events
from tranny.app import torrent_client
from tranny.exceptions import ClientNotAvailable

section_name = 'torrents'
renderer = partial(ui.render, section=section_name)
torrents = Blueprint(section_name, __name__, url_prefix="/torrents")

log = logging.getLogger("web.torrents")


@torrents.route("/")
@renderer("torrents.html")
def index():
    """
    Render the template for the torrents, everything else happens over the API
    """
    pass


@api.on(events.EVENT_TORRENT_RECHECK)
def handle_recheck(message):
    info_hash = message.get('info_hash', [])
    resp = torrent_client.torrent_recheck(info_hash)
    api.emit(events.EVENT_TORRENT_RECHECK_RESPONSE, resp)
    api.flash("Rechecking..!")


@api.on(events.EVENT_TORRENT_ANNOUNCE)
def handle_announce(message):
    """ (re)announce the torrent(s) to the tracker

    :param message:
    :type message: dict
    :return:
    :rtype:
    """
    info_hash = message.get('data', [])
    status = api.STATUS_OK if torrent_client.torrent_reannounce(info_hash) else api.STATUS_FAIL
    api.emit(events.EVENT_TORRENT_ANNOUNCE_RESPONSE, status=status)


@api.on(events.EVENT_TORRENT_LIST)
def handle_list_all():
    """ Return a list of all torrents currently being tracked """
    try:
        torrent_list = torrent_client.torrent_list()
    except ClientNotAvailable as exc:
        api.error_handler(exc, events.EVENT_TORRENT_LIST_RESPONSE)
    else:
        api.emit(events.EVENT_TORRENT_LIST_RESPONSE, data=torrent_list)


@api.on(events.EVENT_TORRENT_STOP)
def handle_stop(message):
    info_hash = message.get('info_hash', [])
    try:
        torrent_client.torrent_stop(info_hash)
    except ClientNotAvailable as exc:
        api.error_handler(exc, events.EVENT_TORRENT_SPEED_RESPONSE)
    else:
        api.emit(events.EVENT_TORRENT_SPEED_RESPONSE, dict(info_hash=info_hash))
        api.flash("Stopped successfully")


@api.on(events.EVENT_TORRENT_START)
def handle_start(message):
    info_hash = message.get('info_hash', [])
    try:
        torrent_client.torrent_start(info_hash)
    except ClientNotAvailable as exc:
        api.error_handler(exc, events.EVENT_TORRENT_START_RESPONSE)
    else:
        api.emit(events.EVENT_TORRENT_START_RESPONSE, dict(info_hash=info_hash))
        api.flash("Started successfully")


@api.on(events.EVENT_TORRENT_DETAILS)
def handle_details(message):
    try:
        info_hash = message.get('info_hash', None)
        data = dict()
        if info_hash:
            data = torrent_client.torrent_status(info_hash)
            status = api.STATUS_OK
        else:
            status = api.STATUS_INCOMPLETE_REQUEST
    except ClientNotAvailable as exc:
        api.error_handler(exc, events.EVENT_TORRENT_DETAILS_RESPONSE)
    else:
        api.emit(events.EVENT_TORRENT_DETAILS_RESPONSE, data=data, status=status)


@api.on(api.EVENT_TORRENT_SPEED)
def handle_speed(message):
    info_hash = message.get('info_hash', None)
    if info_hash:
        tor_speed = torrent_client.torrent_speed(info_hash)
        api.emit(events.EVENT_TORRENT_SPEED_RESPONSE, data=tor_speed)
    else:
        api.emit(events.EVENT_TORRENT_SPEED_RESPONSE, status=api.STATUS_FAIL)


@api.on(events.EVENT_SPEED_OVERALL)
def handle_speed_overall(message=None):
    try:
        up, dn = torrent_client.current_speeds()
    except ClientNotAvailable as exc:
        api.error_handler(exc, events.EVENT_SPEED_OVERALL_RESPONSE)
    else:
        api.emit(events.EVENT_SPEED_OVERALL_RESPONSE, dict(up=up, dn=dn))


@api.on(events.EVENT_TORRENT_FILES)
def handle_files(message):
    info_hash = message.get('info_hash', None)
    tor_files = torrent_client.torrent_files(info_hash)
    api.emit(events.EVENT_TORRENT_FILES_RESPONSE, tor_files)


@api.on(events.EVENT_TORRENT_PEERS)
def handle_peers(message):
    info_hash = message.get('info_hash', None)
    data = torrent_client.torrent_peers(info_hash)
    api.emit(events.EVENT_TORRENT_PEERS_RESPONSE, data=dict(peers=data))


@api.on(events.EVENT_TORRENT_REMOVE)
def handle_remove(message):
    info_hash = message.get('info_hash', None)
    remove_data = message.get('remove_data', False)
    torrent = torrent_client.torrent_status(info_hash)
    if not torrent:
        status = api.STATUS_INVALID_INFO_HASH
    else:
        if torrent_client.torrent_remove(info_hash, remove_data=remove_data):
            status = api.STATUS_OK
        else:
            status = api.STATUS_FAIL
    api.emit(events.EVENT_TORRENT_REMOVE_RESPONSE, data=dict(info_hash=info_hash), status=status)


@api.on(events.EVENT_UPDATE)
def handle_event_update(message):
    e = torrent_client.get_events()
    api.emit(events.EVENT_UPDATE_RESPONSE)
