# -*- coding: utf-8 -*-
"""
Contains functionality related to the websocket API used to communicate with the webui
"""
from __future__ import unicode_literals, absolute_import
from functools import partial
from flask.ext.socketio import emit as sio_emit
from tranny.exceptions import ClientNotAvailable
from tranny.extensions import socketio

NAMESPACE = '/ws'


# General status codes
STATUS_OK = 0
STATUS_FAIL = 1
STATUS_INTERNAL_ERROR = 3

### Specific error codes
# Cant connect to torrent client daemon
STATUS_CLIENT_NOT_AVAILABLE = 5

# Request did not contain enough parameters
STATUS_INCOMPLETE_REQUEST = 10

# Unknown info_hash used in request
STATUS_INVALID_INFO_HASH = 11

# Message levels
MSG_ALERT = 'alert'
MSG_WARN = 'warn'
MSG_INFO = 'info'

# WebSocket event constants
EVENT_TORRENT_RECHECK = 'event_torrent_recheck'
EVENT_TORRENT_RECHECK_RESPONSE = 'event_torrent_recheck_response'

EVENT_TORRENT_ANNOUNCE = 'event_torrent_announce'
EVENT_TORRENT_ANNOUNCE_RESPONSE = 'event_torrent_announce_response'

EVENT_TORRENT_LIST = 'event_torrent_list'
EVENT_TORRENT_LIST_RESPONSE = 'event_torrent_list_response'

EVENT_TORRENT_STOP = 'event_torrent_stop'
EVENT_TORRENT_STOP_RESPONSE = 'event_torrent_stop_response'

EVENT_TORRENT_START = 'event_torrent_start'
EVENT_TORRENT_START_RESPONSE = 'event_torrent_start_response'

EVENT_TORRENT_PEERS = 'event_torrent_peers'
EVENT_TORRENT_PEERS_RESPONSE = 'event_torrent_peers_response'

EVENT_TORRENT_SPEED = 'event_torrent_speed'
EVENT_TORRENT_SPEED_RESPONSE = 'event_torrent_speed_response'

EVENT_TORRENT_FILES = 'event_torrent_files'
EVENT_TORRENT_FILES_RESPONSE = 'event_torrent_files_response'

EVENT_TORRENT_DETAILS = 'event_torrent_details'
EVENT_TORRENT_DETAILS_RESPONSE = 'event_torrent_details_response'

EVENT_TORRENT_REMOVE = 'event_torrent_remove'
EVENT_TORRENT_REMOVE_RESPONSE = 'event_torrent_remove_response'

EVENT_SPEED_OVERALL = 'event_speed_overall'
EVENT_SPEED_OVERALL_RESPONSE = 'event_speed_overall_response'

EVENT_UPDATE = 'event_update'
EVENT_UPDATE_RESPONSE = "event_update_response"

# To send a popup alert to the user
EVENT_ALERT = 'event_alert'

# Generic response
EVENT_RESPONSE = 'event_response'

# Simple partial that includes the default namespace we are using for websocket connections
# This should be used in place of flask.ext.socketio.emit
on = partial(socketio.on, namespace=NAMESPACE)


def error_handler(exc, event_name='internal_error'):
    exc_type = type(exc)
    if exc_type == ClientNotAvailable:
        emit(event_name, {
            'msg': "Client is not available",
            'event': event_name,
            'exc': exc.message,
        }, status=STATUS_CLIENT_NOT_AVAILABLE)
    else:
        emit(event_name, {
            'msg': "Failed to process request, internal error occurred",
            'func': event_name,
            'exc': exc.message,
        }, status=STATUS_INTERNAL_ERROR)


def emit(event, data=None, status=STATUS_OK, **kwargs):
    """ Send a event over websocket to the client

    :param event: Event name as defined in tranny.api
    :type event: basestring
    :param data: Data to send to the client
    :type data: dict
    :param status: Command execution status
    :type status: int
    :param kwargs: Extra arguments to add to the response outside the data param
    :type kwargs: dict
    """
    if data is None:
        data = {}
    sio_emit(event, dict(status=status, data=data, **kwargs))


def flash(message, msg_type=MSG_INFO):
    """ Flash a popup message to the user over the webui

    :param message: Message to broadcast to the user
    :type message: basestring
    :param msg_type: Type of message to send (alert/info/error..)
    :type msg_type: basestring
    """
    emit(EVENT_ALERT, dict(msg=message, msg_type=msg_type))
