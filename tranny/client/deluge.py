# -*- coding: utf-8 -*-
"""
Deluge JSON-RPC client interface

Exposed methods:

[
    'web.get_torrent_info',
    'web.add_torrents',
    'web.get_plugins',
    'web.start_daemon',
    'web.add_host',
    'web.deregister_event_listener',
    'web.register_event_listener',
    'web.get_magnet_info',
    'web.get_torrent_status',
    'auth.delete_session',
    'web.download_torrent_from_url',
    'web.get_config',
    'web.get_hosts',
    'web.disconnect',
    'auth.check_session',
    'web.set_config',
    'auth.login',
    'web.get_plugin_resources',
    'web.upload_plugin',
    'web.connect',
    'web.get_events',
    'auth.change_password',
    'web.get_host_status',
    'web.remove_host',
    'web.connected',
    'web.get_torrent_files',
    'web.stop_daemon',
    'web.update_ui',
    'web.get_plugin_info'
]
"""
from __future__ import unicode_literals, absolute_import, with_statement
import json
from tranny import client
import requests


class DelugeJSONRPCClient(client.ClientProvider):
    _config_key = "deluge-jsonrpc"

    def __init__(self, host='localhost', port=8112, user=None, password='deluge'):
        """

        :param host:
        :type host:
        :param port:
        :type port:
        :param user:
        :type user:
        :param password:
        :type password:
        :return:
        :rtype:
        """
        self._endpoint = 'http://{}:{}/json'.format(host, port)
        self._session = requests.session()
        self._password = password
        self._headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        self._req_id = 0
        self.authenticate()
        self.connect()
        _methods = self._request('system.listMethods')
        print(json.loads(_methods.text)['result'])
        self.client_version()

    def _request(self, method, args=None):
        if not args:
            args = []
        self._req_id += 1
        resp = self._session.post(
            self._endpoint,
            data=json.dumps(dict(method=method, params=args, id=self._req_id)),
            headers=self._headers
        )
        return resp

    def connect(self):
        host_id = json.loads(self._request('web.get_hosts').text)['result'][0][0]
        resp = self._request('web.connect', [host_id])
        _methods = self._request('system.listMethods')
        return resp

    def authenticate(self):
        resp = self._request('auth.login', [self._password])

    def client_version(self):
        version = self._request('core.get_libtorrent_version')
        return version

    def _get_events(self):
        events = self._request('web.get_events')

    def add(self, data, download_dir=None):
        pass

    def list(self):
        """ Get a list of currently loaded torrents from the client

        :return:
        :rtype:
        """
        return []
