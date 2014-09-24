# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import socket
from time import time
from jsonrpclib import Server
from jsonrpclib.jsonrpc import ProtocolError
from tranny import app
from tranny import parser
from tranny import provider
from tranny import constants
from tranny import release
from tranny import net

_errors = {
    -32001: "Invalid API Key",
    -32002: "Call limit exceeded"
}


class BroadcastTheNet(provider.TorrentProvider):
    """
    Provides access to content via BTN's API.
    """

    def __init__(self, config_section="provider_broadcastthenet"):
        super(BroadcastTheNet, self).__init__(config_section)
        self.enabled = app.config.getboolean(self._config_section, "enabled")
        self._api_token = app.config.get(self._config_section, "api_token")
        url = app.config.get(self._config_section, "url")
        self.api = Server(uri=url)

    def __call__(self, method, args=None):
        """ Make a API call to the JSON-RPC server. This method will inject the API key into the request
        automatically for each request.

        :param method: Name of method to execute
        :type method: str
        :param args: dict of arguments to send with request
        :type args: dict
        :return: Server response
        :rtype: str
        """
        result = False
        if not args:
            args = {}
        try:
            response = getattr(self.api, method)(self._api_token, args)
        except ProtocolError as err:
            self._handle_error(err)
        except socket.timeout:
            self.log.warn("Timeout accessing BTN API")
        except socket.error as err:
            self.log.error("There was a socket error trying to call BTN API")
        except Exception as err:
            self.log.exception("Unknown BTN API call error occurred")
        else:
            result = response
        finally:
            return result

    def _handle_error(self, err):
        """

        :param err:
        :type err: ProtocolError
        :return:
        :rtype:
        """
        try:
            msg = _errors[int(err.message[0])]
        except KeyError:
            msg = ""
        self.log.error("JSON-RPC Protocol error calling BTN API: {0}".format(msg))
        if err.message[0] == -32002:
            self.last_update = int(time()) + 300
            self.log.info("Pausing for API cool down")

    def user_info(self):
        return self.__call__(b"userInfo")

    def get_torrents_browse(self, results=100):
        """

        :param results:
        :type results:
        :return:
        :rtype: dict
        """
        return self.__call__("getTorrentsBrowse", results)

    def get_torrent_url(self, torrent_id):
        return self.__call__("getTorrentsUrl", torrent_id)

    def fetch_releases(self, session, scene_only=True):
        """ Generator which yields torrent data to be loaded into backend daemons

        :param session:
        :type session: sqlalchemy.orm.session.Session
        :param scene_only: Only fetch scene releases
        :type scene_only: bool
        :return: Matched Downloaded torrents
        :rtype: TorrentData[]
        """
        found = []
        try:
            releases = self.get_torrents_browse(50)['torrents'].values()
        except (TypeError, KeyError) as err:
            self.log.debug("Failed to fetch releases")
        else:
            if scene_only:
                releases = [rls for rls in releases if rls['Origin'] == "Scene"]
            for entry in releases:
                release_name = entry['ReleaseName']
                release_info = parser.parse_release(release_name, guess_type=constants.MEDIA_TV)
                if not release_info:
                    continue
                section = parser.validate_section(release_info)
                if not section:
                    continue

                if self.exists(session, release_info.release_key) and not self.is_replacement(release_info):
                    continue
                #dl_url = self.get_torrent_url(entry['TorrentID'])
                torrent_data = net.http_request(entry['DownloadURL'], json=False)
                if not torrent_data:
                    self.log.error("Failed to download torrent data from server: {0}".format(entry['link']))
                    continue
                data = release.TorrentData(str(release_name), torrent_data, section)
                yield data, release_info
