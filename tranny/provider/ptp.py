# -*- coding: utf-8 -*-
"""

"""

import requests
from tranny import provider
from tranny import parser
from tranny import datastore
from tranny.app import config
from tranny.exceptions import AuthenticationError, ApiError


class PTP(provider.TorrentProvider):
    """
    Torrent provider over PTP's shitty API

    TODO retry after a while to login after a failure
    """

    def __init__(self, config_section):
        super(PTP, self).__init__(config_section)
        self.endpoint = config.get_default(self._config_section, 'endpoint', 'https://tls.passthepopcorn.me')
        self.enabled = config.getboolean(self._config_section, 'enabled')
        self.interval = config.get_default(self._config_section, 'interval', self.interval, int)
        self._authenticated = False
        self.session = requests.Session()
        if self.enabled:
            self.login()

    def login(self):
        user = config.get_default(self._config_section, 'user', None)
        password = config.get_default(self._config_section, 'password', None)
        passkey = config.get_default(self._config_section, 'passkey', None)
        if not user and password and passkey:
            self.log.warn("Cannot use PTP service, no username or password set")
            return False
        try:
            resp = self.session.post(
                'https://tls.passthepopcorn.me/ajax.php?action=login',
                {
                    'username': user,
                    'password': password,
                    'passkey': passkey,
                    'keeplogged': '1',
                    'login': 'Login'
                }
            )
            if not resp.status_code == 200:
                raise ApiError("Invalid response code received: {}".format(resp.status_code))
            data = resp.json()
            if not data['Result'].upper() == 'OK':
                raise AuthenticationError(data['Message'])
        except (ApiError, AuthenticationError) as err:
            self.log.error(err.message)
        except Exception as err:
            self.log.exception(err)
        else:
            self._authenticated = True
            return self._authenticated

    def find_matches(self):
        if not self._authenticated or not self.enabled:
            return []
        try:
            resp = self.session.get(self.endpoint + '/torrents.php?json=noredirect')
            if "login" in resp.url:
                raise AuthenticationError("Must login to site")
            data = resp.json()
        except requests.ConnectionError as err:
            pass
        else:
            for movie in data['Movies']:
                for torrent in movie['Torrents']:
                    if not torrent['UploadTime'] == movie['LastUploadTime']:
                        continue
                    name = '.'.join([movie['Title'], movie['Year'], torrent['Resolution'], torrent['Codec']])
                    release_name = parser.normalize(name)
                    release_key = datastore.generate_release_key(release_name)
                    if not release_key:
                        continue
                    section = parser.validate_section(release_name)

    def fetch_releases(self, session):
        yield None
