# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from base64 import b64encode
from tranny.app import config, logger
from tranny import client
try:
    from transmissionrpc import Client, TransmissionError
    from transmissionrpc.constants import DEFAULT_PORT
except ImportError:
    logger.error("""Please install the transmission python library available at
        "http://pythonhosted.org/transmissionrpc/""")
    raise SystemExit()


class TransmissionClient(client.ClientProvider):
    _config_key = "transmission"

    def __init__(self, host=None, port=None, user=None, password=None):
        if not host:
            host = config.get_default(self._config_key, "host", "localhost")
        self.host = host
        if not port:
            port = config.get_default(self._config_key, "port", DEFAULT_PORT, int)
        self.port = port
        if not user:
            user = config.get_default(self._config_key, "user", None)
        self.user = user
        if not password:
            password = config.get_default(self._config_key, "password", None)
        self.password = password
        self.connect()

    def client_version(self):
        return "Transmission XX"

    def connect(self):
        try:
            self.client = Client(self.host, port=self.port, user=self.user, password=self.password)
        except TransmissionError as err:
            if err.original.code == 111:
                logger.error("Failed to connect to transmission-daemon, is it running?")
            else:
                logger.exception("Error connecting to transmission server")

    def add(self, data, download_dir=None):
        try:
            encoded_data = b64encode(data)
            res = self.client.add(encoded_data, download_dir=download_dir)
        except TransmissionError, err:
            try:
                msg = err._message
            except AttributeError:
                msg = err.message
            if "duplicate torrent" in msg:
                logger.warning("Tried to add duplicate torrent file")
                return True
            logger.exception(err)
            return False

        return res

    def add_uri(self, uri):
        torrent = self.client.add_uri(uri=uri)
        return torrent

    def info(self, torrent_id):
        torrent_info = self.client.info(torrent_id)
        return torrent_info

    def list(self):
        """ Get a list of currently loaded torrents from the client

        :return:
        :rtype:
        """
        return self.client.list()

    def remove(self, torrent_id):
        """ Remove a torrent from the backend client via its torrentID supplied by the
        torrent daemon

        :param torrent_id: TorrentID provided by transmission
        :type torrent_id: int
        :return:
        :rtype:
        """
        return self.client.remove(torrent_id)
