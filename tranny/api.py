# -*- coding: utf-8 -*-
"""
Contains functionality related to the websocket API used to communicate with the webui
"""

from functools import partial
from flask.ext.socketio import emit as sio_emit
from tranny import events
from tranny.exceptions import ClientNotAvailable
from tranny.extensions import socketio

# Default websocket namespace for the websocket connection
NAMESPACE = '/ws'

# General status codes
STATUS_OK = 0
STATUS_FAIL = 1
STATUS_INTERNAL_ERROR = 3

### Specific error status codes
# Cant connect to torrent client daemon
STATUS_CLIENT_NOT_AVAILABLE = 5

# Request did not contain enough parameters
STATUS_INCOMPLETE_REQUEST = 10

# Unknown info_hash used in request
STATUS_INVALID_INFO_HASH = 11

# Message levels, should correspond to css class names
MSG_ALERT = 'alert'
MSG_WARN = 'warn'
MSG_INFO = 'info'

# Simple partial that includes the default namespace we are using for websocket connections
# This should be used in place of flask.ext.socketio.emit
on = partial(socketio.on, namespace=NAMESPACE)


def error_handler(exc, event_name='internal_error'):
    """ Generate API error events to send to the client on an error

    :param exc: Exception raised during handling the event
    :type exc: Exception
    :param event_name: Name of the event being handled
    :type event_name: basestring
    """
    exc_type = type(exc)
    if exc_type == ClientNotAvailable:
        emit(event_name, {
            'msg': "Client is not available",
            'event': event_name,
            'exc': "{}".format(exc),
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


def flash(message, msg_type=MSG_INFO, ttl=5):
    """ Flash a popup message to the user over the webui

    :param ttl: Duration of the popup
    :type ttl: int
    :param message: Message to broadcast to the user
    :type message: basestring
    :param msg_type: Type of message to send (alert/info/error..)
    :type msg_type: basestring
    """
    emit(events.EVENT_ALERT, dict(msg=message, msg_type=msg_type, ttl=ttl))
