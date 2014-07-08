# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
try:
    import http.client as httplib
except ImportError:
    import httplib
from collections import namedtuple
from logging import getLogger
from requests import Session
from requests.auth import HTTPBasicAuth
from tranny import app, exceptions, client


class uTorrentException(exceptions.TrannyException):
    pass


class InvalidToken(uTorrentException):
    pass


class url_args(dict):
    def __str__(self):
        return "&".join(["{0}={1}".format(k, v) for k, v in self.items()])


UTSetting = namedtuple("UTSetting", ["name", "int", "str", "access"])


class UTorrentClient(client.ClientProvider):
    """
    A basic uTorrent WebUI API client.

    Warning: this client is the most fragile of the bunch due to a lack of a proper
    API to use. Its recommended if possible to use one of the other clients instead
    due to these design issues.
    """
    version = None
    _config_key = "utorrent"
    _url_prefix = "/gui"
    _token = False

    def __init__(self, host=None, port=None, user=None, password=None):
        """ Setup the connection parameters and verify connection

        :param host: uTorrent webui host
        :type host: str
        :param port: webui port
        :type port: int
        :param user: webui username
        :type user: str
        :param password: webui password
        :type password: str
        """
        self.log = getLogger("rpc.utorrent")
        if not host:
            host = app.config.get_default(self._config_key, "host", "localhost")
        self.host = host
        if not port:
            port = app.config.getint(self._config_key, "port")
        self.port = port
        if not user:
            user = app.config.get_default(self._config_key, "user", None)
        self.user = user
        if not password:
            password = app.config.get_default(self._config_key, "password", None)
        self.password = password
        self._session = Session()
        self.config = app.config
        self._token = None
        version = self.get_version()
        self.log.info("Connected to uTorrent build {0}".format(version))

    def _fetch(self, url="/", args=None, json=True, token=True, resend=False):
        """ Fetch data from the uTorrent API.

        :param url: URL to request. The self._urlprefix value will be prefixed to this value
        :type url: str
        :param args: dict of url keyword arguments
        :type args: dict
        :param json: Should the request be decoded as json
        :type json: bool
        :param token: Send the AuthToken along with the request?
        :type token: bool
        :param resend: Is this a second attempt to handle a new token
        :type resend: bool
        :return: server response
        :rtype: str, dict
        """
        url = "http://{0}:{1}{2}{3}".format(self.host, self.port, self._url_prefix, url)
        full_args = url_args()
        if token:
            full_args['token'] = self.token
        if args:
            full_args.update(args)
        if full_args:
            url = "{0}?{1}".format(url, full_args)
        result = self._session.get(
            url,
            auth=HTTPBasicAuth(self.user, self.password),
            proxies=self.config.get_proxies()
        )
        if result.status_code == httplib.MULTIPLE_CHOICES:  # 300
            if resend:
                raise InvalidToken("Unable to fetch new AuthToken")
            return self._fetch(url, args=args, json=json, token=token, resend=True)
        if result and not json:
            result = result.content
        elif result and json:
            try:
                result = result.json
            except Exception as err:
                self.log.exception("Failed to decode response to json")
                raise
        return result

    @property
    def token(self, force_update=False):
        """ Fetch the AuthToken from the API

        :param force_update: Force a refresh of the current API token
        :type force_update: bool
        :return: Token parsed from page
        :rtype: str
        """
        if not self._token or force_update:
            body = self._fetch("/token.html", json=False, token=False)
            match = re.search(r"<div id='token' style='display:none;'>([^<>]+)</div>", body, re.I | re.M)
            if not match:
                raise AttributeError("Failed to find utorrent token")
            token = match.group(1)
            assert len(token) == 64, "Invalid token received"
            self._token = token
        return self._token

    def get_version(self):
        """ Fetch the version (build) of utorrent connected.

        :return: Connected uTorrent build number
        :rtype: int
        """
        if not self.version:
            response = self._fetch(args={'action': "getsettings"})
            version = response["build"]
            self.version = version
        return self.version

    def list(self):
        torrent_list = self._fetch(args={"list": 1})
        return torrent_list

    def _action(self, action, args=None):
        full_args = {'action': action}
        if args:
            full_args.update(args)
        return self._fetch(args=full_args)

    def get_settings(self, key=None):
        value = self._action("getsettings")
        settings = {}
        for args in value['settings']:
            settings[args[0]] = UTSetting(*args)
        if key:
            return settings[key]
        return settings

    def set_setting(self, settings):
        """

        :param settings:
        :type settings: dict
        :return:
        :rtype:
        """
        for setting, value in settings.items():
            self.log.debug("Updating setting: {} = {}".format(setting, value))
            self._action("setsetting", args={"s": setting, "v": value})

    def add(self, data, download_dir=None):
        if download_dir:
            old_dir = self.get_settings("dir_active_download")
            self.set_setting({"dir_active_download": download_dir})
            new_dir = self.get_settings("dir_active_download").str
        url = "http://{0}:{1}{2}/?action=add-file&token={3}".format(
            self.host, self.port, self._url_prefix, self.token
        )
        response = self._session.post(
            url,
            auth=HTTPBasicAuth(self.user, self.password),
            files={'torrent_file': ('torrent_file.torrent', data)},
            proxies=self.config.get_proxies()
        )
        if response.status_code != httplib.OK:

            self.log.error("Got invalid request from client: {0}".format(response.json.error))
        else:
            try:
                self.log.warning(response.json['error'])
            except KeyError:
                pass
        return response.status_code == httplib.OK

