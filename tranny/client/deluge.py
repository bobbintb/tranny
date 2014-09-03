# -*- coding: utf-8 -*-
"""
Deluge JSON-RPC client interface

.. note::
    This was the first complete implementation of the backend client, thus the other backends have been
    somewhat molded to fit deluge's definition of data structures
"""
from __future__ import unicode_literals, absolute_import, with_statement
import json
import time
import gevent
import requests
from tranny import client, app, util
from tranny.exceptions import AuthenticationError, ApiError, ClientNotAvailable

ERROR_AUTH = 1
ERROR_UNKNOWN_METHOD = 2


class DelugeClient(client.TorrentClient):
    """
    API client for deluge
    """

    # Configuration file section name
    config_key = "deluge"

    # Number of request retry attempts to allow
    max_request_retries = 1

    allowed_pre_connect_methods = ('web.connect', 'web.auth', 'web.get_hosts')

    def __init__(self, host='localhost', port=8112, password='deluge'):
        """ Roughly the order of requests used in the built in deluge webui that we emulate

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

        If the password is not accepted _valid_password will be set to false and prevent any
        more requests from happening.

        :param host: Host of the deluge webui
        :type host: basestring
        :param port: Port of the webui (default: 8112)
        :type port: int
        :param password: Password to the webui (default: deluge)
        :type password: string
        """
        super(DelugeClient, self).__init__()
        self._endpoint = 'http://{}:{}/json'.format(host, port)
        self._session = requests.session()
        self._password = password
        self._headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        self._req_id = 0
        self._valid_password = True
        self._last_request = 0
        self._host_up = True
        self._host_check = gevent.Greenlet(self._check_conn)
        self._host_check.start()

    def _check_conn(self):
        while True:
            try:
                self._request('web.get_hosts')
            except (requests.ConnectionError, ClientNotAvailable) as err:
                #app.logger.debug("Failed to connect to {}".format(
                #    app.config.get_default("general", "client", "torrent client")))
                self._host_up = False
                sleep_time = 1
            else:
                self._host_up = True
                sleep_time = 30
            gevent.sleep(sleep_time)

    def _request(self, method, args=None, attempt=0):
        # Prevent requests other than ones used to connect while not connected
        # if not self.connected and not method in self.allowed_pre_connect_methods:
        #    return False
        if not self._host_up:
            raise ClientNotAvailable()
        if attempt > self.max_request_retries:
            self.log.error("Maximum number of retries reached: {} ({})".format(
                method, self.max_request_retries))
            return False
        if not args:
            args = []
        self._req_id += 1
        self.log.debug("{} {}".format(method, args))
        ret_val = None
        try:
            resp = self._session.post(
                self._endpoint,
                data=json.dumps(dict(method=method, params=args, id=self._req_id)),
                headers=self._headers
            )
        except requests.ConnectionError:
            self._host_up = False
            raise ClientNotAvailable()
        try:
            resp = json.loads(resp.text)
            error = resp.get('error', False)
            if error:
                if error['code'] == ERROR_AUTH:
                    raise AuthenticationError(error)
                else:
                    raise ApiError(error)
        except AuthenticationError:
            # Try to authenticate, otherwise mark our password as bad
            # and don't send any new requests
            if not self.authenticate():
                self._valid_password = False
            if not self._valid_password:
                ret_val = False
            else:
                # Add this after our authentication request as its the seemingly normal
                # sequence of events, This could possibly be the wrong location.
                if not self.is_connected():
                    self.connect()
                return self._request(method, args=args, attempt=attempt + 1)['result']
        except ApiError as err:
            self.log.error(err)
        except Exception as exc:
            self.log.exception(exc)
        else:
            ret_val = resp['result']
        finally:
            return ret_val

    def is_connected(self):
        return self._request('web.connected')

    def connect(self):
        """ Establish a "connection" to the deluge/webui service. This grants us access to all available
        exposed api methods from deluge. The client must authenticate() before trying to connect().

        :return: Connection attempt result
        :rtype: bool
        """
        host_id = self._request('web.get_hosts')[0][0]
        resp = self._request('web.connect', [host_id])
        if resp is None:
            # Flag us as connected, allowing further api requests
            self.connected = True
            app.logger.info("Connected to deluge {}/{}".format(*self.client_version()))
            self._request('web.register_event_listener', ['PluginDisabledEvent'])
            self._request('web.register_event_listener', ['PluginEnabledEvent'])
            self._request('web.register_event_listener', ['TorrentAddedEvent'])
            self._request('web.register_event_listener', ['TorrentStateChangedEvent'])
            self._request('web.register_event_listener', ['TorrentResumedEvent'])
        else:
            self._last_request = time.time()
        return resp

    def authenticate(self):
        return self._request('auth.login', [self._password])

    def client_version(self):
        daemon_version = self._request('daemon.info')
        libtorrent_version = self._request('core.get_libtorrent_version')
        return ", ".join([daemon_version, libtorrent_version])

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

    def current_speeds(self):
        resp = self._request('web.update_ui', [['upload_rate', 'download_rate'], {}])
        try:
            return resp['stats']['upload_rate'], resp['stats']['download_rate']
        except:
            return 0.0, 0.0

    def torrent_list(self):
        """ Get a list of currently loaded torrents from the client

        :return:
        :rtype:
        """
        resp = self._request(
            'web.update_ui', [
                [
                    "queue", "name", "total_size", "state", "progress", "num_seeds",
                    "total_seeds", "num_peers", "total_peers", "download_payload_rate",
                    "upload_payload_rate", "eta", "ratio", "distributed_copies",
                    "is_auto_managed", "time_added", "tracker_host", "save_path", "total_done",
                    "total_uploaded", "max_download_speed", "max_upload_speed", "seeds_peers_ratio"
                ], {}
            ]
        )
        torrent_data = list()
        if not resp:
            return torrent_data
        for info_hash, detail in resp.get('torrents', {}).items():
            torrent_info = client.ClientTorrentData(
                info_hash,
                detail['name'],
                detail['ratio'],
                detail['upload_payload_rate'],
                detail['download_payload_rate'],
                detail['total_uploaded'],
                detail['total_done'],
                detail['total_size'],
                detail['total_done'],
                detail['num_peers'],
                detail['total_peers'],
                detail['num_seeds'],
                detail['total_seeds'],
                '1',
                '1',
                detail['state'],
                detail['progress']
            )
            torrent_data.append(torrent_info)
        return torrent_data

    def torrent_speed(self, info_hash):
        return self._request('web.get_torrent_status', [info_hash, ["download_payload_rate", "upload_payload_rate"]])

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
        return self._request('core.force_reannounce', [info_hash]) is None

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
        return self._request('web.disconnect')

    def get_events(self):
        resp = self._request('web.get_events')
        return resp
