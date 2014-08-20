# -*- coding: utf-8 -*-
"""
Endpoints for the /torrent sections
"""
from __future__ import unicode_literals
from functools import partial
from flask import Blueprint, current_app, request
from flask.ext.socketio import emit, error
from tranny import ui, api
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
    resp = current_app.services.client.torrent_recheck(info_hash)
    emit(api.Event.RESPONSE, dict(data=resp))


@socketio.on(api.EVENT_TORRENT_ANNOUNCE, namespace=socketio_namespace)
def reannounce(message):
    info_hash = message.get('data', [])
    resp = current_app.services.client.torrent_reannounce(info_hash) is None
    emit(api.Event.RESPONSE, dict(data=resp))


@torrents.route("/list")
@renderer(fmt='json')
def list():
    """ To be migrated to socketio..

    :return:
    :rtype:
    """
    return dict(data=current_app.services.client.torrent_list())


@socketio.on(api.EVENT_TORRENT_STOP)
def stop():
    current_app.services.client.torrent_stop(request.json)
    return dict(status=0)


@socketio.on(api.EVENT_TORRENT_START)
def start(message):
    current_app.services.client.torrent_start(message.get('info_hash', []))
    return dict(status=0)


@socketio.on(api.EVENT_TORRENT_DETAILS)
def details(message):
    info_hash = message.get('info_hash', None)
    if info_hash:
        resp = current_app.services.client.torrent_status(info_hash)
        status = api.STATUS_OK
    else:
        status = api.STATUS_INCOMPLETE_REQUEST
    emit(api.EVENT_RESPONSE, dict(data=resp, status=status))


@socketio.on(api.EVENT_TORRENT_SPEED)
@renderer(fmt='json')
def speed(info_hash):
    resp = current_app.services.client.torrent_speed(info_hash)
    return resp


@torrents.route('/<string(length=40):info_hash>/files')
def files(info_hash):
    resp = current_app.services.client.torrent_files(info_hash)
    return resp


@torrents.route('/<string(length=40):info_hash>/peers')
@renderer(fmt='json')
def peers(info_hash):
    resp = current_app.services.client.torrent_peers(info_hash)
    return resp


@torrents.route('/<string(length=40):info_hash>', methods=['DELETE'])
@torrents.route('/<string(length=40):info_hash>/<remove_data>', methods=['DELETE'])
def remove(info_hash, remove_data=False):
    torrent = current_app.services.client.torrent_status(info_hash)
    if not torrent:
        status = api.NOT_FOUND
    else:
        if current_app.services.client.torrent_remove(info_hash, remove_data=remove_data):
            status = api.NO_CONTENT
        else:
            status = api.INTERNAL_SERVER_ERROR
    return api.response(status=status, json=False)
