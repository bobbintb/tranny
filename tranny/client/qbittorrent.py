# -*- coding: utf-8 -*-
"""
Deluge JSON-RPC client interface

.. note::
    This was the first complete implementation of the backend client, thus the other backends have been
    somewhat molded to fit deluge's definition of data structures
"""
from __future__ import unicode_literals, absolute_import, with_statement
import json
import requests
from requests import auth
from tranny import client
from tranny import net
from tranny.exceptions import AuthenticationError, ApiError
try:
    from http import client as httplib
except ImportError:
    import httplib

ERROR_AUTH = 1
ERROR_UNKNOWN_METHOD = 2


class QBittorrentClient(client.TorrentClient):
    """
    API client for deluge
    """

    # Configuration file section name
    config_key = "client_qbittorrent"

    # Number of request retry attempts to allow
    max_request_retries = 1

    def __init__(self, host='localhost', port=8080, user='admin', password=''):
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
        super(QBittorrentClient, self).__init__()
        self._endpoint = 'http://{}:{}/json'.format(host, port)
        self._session = requests.session()
        self._session.auth = auth.HTTPDigestAuth(user, password)
        self._headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        self._req_id = 0
        self._valid_password = True
        self._last_request = 0

    def _request(self, method, args=None, attempt=0, req_type='get'):
        # Prevent requests other than ones used to connect while not connected
        # if not self.connected and not method in self.allowed_pre_connect_methods:
        #    return False
        if attempt > self.max_request_retries:
            self.log.error("Maximum number of retries reached: {} ({})".format(
                method, self.max_request_retries))
            return False
        if not args:
            args = []
        self._req_id += 1
        self.log.debug("{} {}".format(method, args))
        method_endpoint = self._endpoint + method
        if req_type == 'get':
            resp = self._session.get(method_endpoint)
        else:
            resp = self._session.post(method_endpoint, data=args)
        resp_data = None
        try:
            if resp.status_code == httplib.OK:
                resp_data = json.loads(resp.text)
            elif resp.status_code == httplib.UNAUTHORIZED:
                raise AuthenticationError("Authorization unaccepted")
            else:
                raise ApiError("blah..")
        except AuthenticationError as err:
            # Try to authenticate, otherwise mark our password as bad
            # and don't send any new requests
            resp_data = {'error': err.message}
            self._valid_password = False
        except ApiError as err:
            resp_data = {'error': err.message}
            self.log.error(err)
        except Exception as exc:
            self.log.exception(exc)
        finally:
            return resp_data

    def is_connected(self):
        return False

    def client_version(self):
        return "qbt..."

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
        resp = self._request('/transferInfo')
        return resp['up_info'], resp['dl_info']

    def torrent_list(self):
        """ Get a list of currently loaded torrents from the client

            :return:
        :rtype:
        """
        resp = self._request('/torrents')
        return resp

    @staticmethod
    def parse_torrent_info(torrent):
        up_rate = net.parse_net_speed_value(torrent['upspeed'])
        dn_rate = net.parse_net_speed_value(torrent['dlspeed'])
        size = net.parse_net_speed_value(torrent['size'])
        num_leechers, total_leechers = torrent['num_leechs'].split()
        total_leechers = total_leechers.strip("()")
        num_peers, total_peers = torrent['num_seeds'].split()
        total_peers = total_peers.strip("()")
        completed = size * torrent['progress']
        info = client.ClientTorrentData(
            torrent['hash'],
            torrent['name'],
            torrent['ratio'],
            up_rate,
            dn_rate,
            0,
            0,
            size,
            completed,
            num_leechers,
            total_leechers,
            num_peers,
            total_peers,
            torrent['priority'],
            None,
            None,
            torrent['progress']
        )
        return info

    def torrent_speed(self, info_hash):
        resp = self._request('/torrents')
        return 0.0, 0.0

    def torrent_status(self, info_hash):
        return {}

    def torrent_pause(self, info_hash):
        resp = self._request('/command/pause', {'hash': info_hash}, req_type='post')
        return resp

    def torrent_pause_all(self):
        return self._request('/command/pauseAll')

    def torrent_start(self, info_hash):
        resp = self._request('/command/resume', {'hash': info_hash}, req_type='post')
        return resp

    def torrent_start_all(self, info_hash):
        resp = self._request('/command/resumeall', req_type='post')
        return resp

    def torrent_remove(self, info_hash, remove_data=False):
        if remove_data:
            resp = self._request('/command/deletePerm', {'hashes': info_hash}, req_type='post')
        else:
            resp = self._request('/command/delete', {'hashes': info_hash}, req_type='post')
        return resp

    def torrent_reannounce(self, info_hash):
        return self._request('core.force_reannounce', [info_hash]) is None

    def torrent_recheck(self, info_hash):
        return self._request('/command/recheck', {'hash': info_hash})

    def torrent_files(self, info_hash):
        resp = self._request('/propertiesFiles/'+info_hash)
        return resp

    def torrent_add(self, info_hash):
        resp = self._request('web.add_torrents', [info_hash])
        return resp

    def torrent_peers(self, info_hash):
        resp = self._request('web.get_torrent_status', [info_hash, ['peers']])
        return resp

    def disconnect(self):
        pass

    def get_events(self):
        resp = self._request('web.get_events')
        return resp
