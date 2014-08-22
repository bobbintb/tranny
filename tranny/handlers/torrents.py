# -*- coding: utf-8 -*-
"""
Endpoints for the /torrent sections
"""
from __future__ import unicode_literals
from functools import partial
from flask import Blueprint, current_app, request
from flask.ext.socketio import emit, error
from tranny import ui, api
from tranny import client
from tranny.extensions import socketio

section_name = 'torrents'
renderer = partial(ui.render, section=section_name)
torrents = Blueprint(section_name, __name__, url_prefix="/torrents")
socketio_namespace = '/ws'


@torrents.route("/")
@renderer("torrents.html")
def index():
    return dict()


@socketio.on(api.EVENT_TORRENT_RECHECK, namespace=socketio_namespace)
def recheck(message):
    info_hash = message.get('info_hash', [])
    resp = client.get().torrent_recheck(info_hash)
    emit(api.EVENT_RESPONSE, dict(data=resp))


@socketio.on(api.EVENT_TORRENT_ANNOUNCE, namespace=socketio_namespace)
def announce(message):
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
    emit(api.EVENT_RESPONSE, dict(status=status))


@socketio.on(api.EVENT_TORRENT_LIST, namespace=socketio_namespace)
def list_all():
    """ Return a list of all torrents currently being tracked """
    torrent_list = client.get().torrent_list()
    emit(api.EVENT_TORRENT_LIST_RESPONSE, dict(data=torrent_list))


@socketio.on(api.EVENT_TORRENT_STOP, namespace=socketio_namespace)
def stop(message):
    info_hash = message.get('info_hash', [])
    client.get().torrent_stop(info_hash)
    emit(api.EVENT_TORRENT_SPEED_RESPONSE, dict(info_hash=info_hash))


@socketio.on(api.EVENT_TORRENT_START, namespace=socketio_namespace)
def start(message):
    info_hash = message.get('info_hash', [])
    client.get().torrent_start(info_hash)
    emit(api.EVENT_TORRENT_SPEED_RESPONSE, dict(info_hash=info_hash))


@socketio.on(api.EVENT_TORRENT_DETAILS, namespace=socketio_namespace)
def details(message):
    info_hash = message.get('info_hash', None)
    data = dict()
    if info_hash:
        data = client.get().torrent_status(info_hash)
        status = api.STATUS_OK
    else:
        status = api.STATUS_INCOMPLETE_REQUEST
    emit(api.EVENT_TORRENT_DETAILS_RESPONSE, dict(data=data, status=status))


@socketio.on(api.EVENT_TORRENT_SPEED, namespace=socketio_namespace)
def speed(message):
    info_hash = message.get('info_hash', None)
    if info_hash:
        tor_speed = client.get().torrent_speed(info_hash)
        emit(api.EVENT_TORRENT_SPEED_RESPONSE, dict(data=tor_speed, status=api.STATUS_OK))
    else:
        emit(api.EVENT_TORRENT_SPEED_RESPONSE, dict(status=api.STATUS_FAIL))


@socketio.on(api.EVENT_SPEED_OVERALL, namespace=socketio_namespace)
def speed_overall(message=None):
    up, dn = client.get().current_speeds()
    emit(api.EVENT_SPEED_OVERALL_RESPONSE, dict(data=dict(up=up, dn=dn)))


@socketio.on(api.EVENT_TORRENT_FILES, namespace=socketio_namespace)
def files(message):
    info_hash = message.get('info_hash', None)
    tor_files = client.get().torrent_files(info_hash)
    emit(api.EVENT_TORRENT_FILES_RESPONSE, dict(status=api.STATUS_OK, data=tor_files))


@socketio.on(api.EVENT_TORRENT_PEERS, namespace=socketio_namespace)
def peers(message):
    info_hash = message.get('info_hash', None)
    data = client.get().torrent_peers(info_hash)
    emit(api.EVENT_TORRENT_PEERS_RESPONSE, dict(status=api.STATUS_OK, data=data))


@socketio.on(api.EVENT_TORRENT_REMOVE, namespace=socketio_namespace)
def remove(message):
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
