import socket
from time import time
from jsonrpclib import Server
from jsonrpclib.jsonrpc import ProtocolError
from tranny.parser import match_release
from tranny.provider import TorrentProvider
from tranny.release import TorrentData
from tranny.datastore import generate_release_key

_errors = {
    -32002: "Call limit exceeded"
}


class BroadcastTheNet(TorrentProvider):
    def __init__(self, config, config_section="service_broadcastthenet"):
        super(BroadcastTheNet, self).__init__(config, config_section)
        self._api_token = config.get(self._config_section, "api_token")
        url = config.get(self._config_section, "url")
        self.api = Server(uri=url)
        self.log.info("Initialized BTN provider")

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
            msg = _errors[err.message[0]]
        except KeyError:
            msg = ""
        self.log.error("JSON-RPC Protocol error calling BTN API: {0}".format(msg))
        if err.message[0] == -32002:
            self.last_update = int(time()) + 300
            self.log.info("Pausing for API cool down")

    def user_info(self):
        return self.__call__("userInfo")

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

    def fetch_releases(self, scene_only=True):
        """ Generator which yields torrent data to be loaded into backend daemons

        :param scene_only: Only fetch scene releases
        :type scene_only: bool
        :return: Matched Downloaded torrents
        :rtype: TorrentData[]
        """
        try:
            releases = self.get_torrents_browse(20)['torrents'].values()
        except (TypeError, KeyError) as err:
            self.log.debug("Failed to fetch releases")
        else:
            if scene_only:
                releases = [rls for rls in releases if rls['Origin'] == "Scene"]
            for entry in releases:
                release_name = entry['ReleaseName']
                release_key = generate_release_key(release_name)
                if not release_key:
                    continue
                section = match_release(self.config, release_name)
                if not section:
                    continue
                if self.exists(release_key):
                    if self.config.get_default("general", "fetch_proper", True, bool):
                        if not ".proper." in release_name.lower():
                            # Skip releases unless they are considered proper's
                            self.log.debug(
                                "Skipped previously downloaded release ({0}): {1}".format(
                                    release_key,
                                    release_name
                                )
                            )
                            continue
                dl_url = self.get_torrent_url(entry['TorrentID'])
                torrent_data = self._download_url(dl_url)
                if not torrent_data:
                    self.log.error("Failed to download torrent data from server: {0}".format(entry['link']))
                    continue
                yield TorrentData(str(release_name), torrent_data, section)
