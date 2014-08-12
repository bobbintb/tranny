# -*- coding: utf-8 -*-
"""
Deluge JSON-RPC client interface

"""
from __future__ import unicode_literals, absolute_import, with_statement
import json
import time
import logging
import requests
from tranny import client, app


class DelugeClient(client.TorrentClient):
    """
    API client for deluge
    """
    config_key = "deluge"

    def __init__(self, host='localhost', port=8112, password='deluge'):
        """

        roughly the order of requests used in the built in webui

        1. system.listMethods
        2. auth.check_session: []
        3. web.register_event_listener [PluginDisabledEvent]
        4. web.register_event_listener [PluginEnabledEvent]
        5. web.get_events []
        6. web.connected []
        7. web.update_ui [["queue","name","total_size","state","progress","num_seeds",
            "total_seeds","num_peers","total_peers","download_payload_rate","upload_payload_rate",
            "eta","ratio","distributed_copies","is_auto_managed","time_added","tracker_host",
            "save_path","total_done","total_uploaded","max_download_speed","max_upload_speed",
            "seeds_peers_ratio"],{}]
        8. web.get_plugins
        9. web.update_ui
        10. web.get_events [] (periodic?)

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
        self._last_request = 0
        self._is_connected = False
        self.log = logging.getLogger(__name__)
        self.authenticate()
        self.connect()

    def _request(self, method, args=None):
        if not args:
            args = []
        self._req_id += 1
        resp = self._session.post(
            self._endpoint,
            data=json.dumps(dict(method=method, params=args, id=self._req_id)),
            headers=self._headers
        )
        try:
            return json.loads(resp.text)['result']
        except:
            return None

    def connect(self):
        host_id = self._request('web.get_hosts')[0][0]
        resp = self._request('web.connect', [host_id])
        if resp is None:
            self._is_connected = True
            app.logger.info("Connected to deluge {}/{}".format(*self.client_version()))
            self._request('register_event_listener', ['PluginDisabledEvent'])
            self._request('register_event_listener', ['PluginEnabledEvent'])
        else:
            self._last_request = time.time()
        return resp

    def authenticate(self):
        resp = self._request('auth.login', [self._password])
        return resp

    def client_version(self):
        daemon_version = self._request('daemon.info')
        libtorrent_version = self._request('core.get_libtorrent_version')
        return daemon_version, libtorrent_version

    def _get_events(self):
        events = self._request('web.get_events')

    def get_capabilities(self):
        """ Return a list of supported methods of the client. This is used to tell the
         webui what the client supports instead of having to hardcode things on a per
         client basis

        :return: List of supported functions
        :rtype: str[]
        """
        return ['torrent_add', 'torrent_list']

    def torrent_add(self, data, download_dir=None):
        pass

    def torrent_list(self):
        """ Get a list of currently loaded torrents from the client

        :return:
        :rtype:
        """
        resp = self._request(
            'web.update_ui', [
                ["queue", "name", "total_size", "state", "progress", "num_seeds",
                 "total_seeds", "num_peers", "total_peers", "download_payload_rate",
                 "upload_payload_rate", "eta", "ratio", "distributed_copies",
                 "is_auto_managed", "time_added", "tracker_host", "save_path", "total_done",
                 "total_uploaded", "max_download_speed", "max_upload_speed", "seeds_peers_ratio"
                ], {}]
        )
        torrent_data = list()
        for info_hash, detail in resp.get('torrents', {}).items():
            torrent_info = client.ClientTorrentData(
                info_hash,
                detail['name'],
                self._fmt_ratio(detail['ratio']),
                detail['upload_payload_rate'],
                detail['download_payload_rate'],
                detail['total_uploaded'],
                detail['total_done'],
                detail['total_size'],
                detail['total_done'],
                detail['num_peers'],
                detail['total_peers'],
                '1',
                '1',
                detail['state']
            )
            torrent_data.append(torrent_info)
        return torrent_data

    def torrent_status(self, info_hash):
        params = [
            "total_done", "total_payload_download", "total_uploaded", "total_payload_upload",
            "next_announce", "tracker_status", "num_pieces", "piece_length", "is_auto_managed",
            "active_time", "seeding_time", "seed_rank", "queue", "name", "total_size", "state",
            "progress", "num_seeds", "total_seeds", "num_peers", "total_peers",
            "download_payload_rate", "upload_payload_rate", "eta", "ratio", "distributed_copies",
            "is_auto_managed", "time_added", "tracker_host", "save_path", "total_done", "total_uploaded",
            "max_download_speed", "max_upload_speed", "seeds_peers_ratio"
        ]
        resp = self._request('web.get_torrent_status', [info_hash, params])
        return resp


    def torrent_pause(self, info_hash):
        resp = self._request('core.pause_torrent', [info_hash])
        return resp is None

    # deluge doesnt have a notion of "stop"
    torrent_stop = torrent_pause

    def torrent_start(self, info_hash):
        resp = self._request('core.resume_torrent', [info_hash])
        return resp

    def torrent_remove(self, info_hash, remove_data=False):
        resp = self._request('core.remove_torrent', [info_hash, remove_data])
        return resp

    def torrent_reannounce(self, info_hash):
        resp = self._request('core.force_reannounce', [info_hash])
        return resp

    def torrent_recheck(self, info_hash):
        resp = self._request('core.force_recheck', [info_hash])
        return resp

    def torrent_files(self, info_hash):
        resp = self._request('web.get_torrent_files', [info_hash])
        return resp

    def torrent_add(self, info_hash):
        resp = self._request('web.add_torrents', [info_hash])
        return resp

    def torrent_peers(self, info_hash):
        resp = self._request('web.get_torrent_status', [info_hash, ['peers']])
        return resp

    def disconnect(self):
        resp = self._request('web.disconnect')
        return resp
