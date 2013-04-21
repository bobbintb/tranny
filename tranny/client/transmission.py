from logging import getLogger
from base64 import b64encode
from tranny.client import ClientProvider

log = getLogger("rpc.transmission")

try:
    from transmissionrpc import Client, TransmissionError
    from transmissionrpc.constants import DEFAULT_PORT
except ImportError, err:
    log.error("""Please install the transmission python library available at
        "http://pythonhosted.org/transmissionrpc/""")
    raise SystemExit(err)


class TransmissionClient(ClientProvider):
    _config_key = "transmission"

    def __init__(self, config, host=None, port=None, user=None, password=None):
        if not host:
            host = config.get_default(self._config_key, "host", "localhost")
        if not port:
            port = config.get_default(self._config_key, "port", DEFAULT_PORT, int)
        if not user:
            user = config.get_default(self._config_key, "user", None)
        if not password:
            password = config.get_default(self._config_key, "password", None)
        self.client = Client(host, port=port, user=user, password=password)
        self.log = log

    def add(self, data, download_dir=None):
        try:
            encoded_data = b64encode(data)
            res = self.client.add(encoded_data, download_dir=download_dir)
        except TransmissionError, err:
            if "duplicate torrent" in err._message:
                self.log.warning("Tried to add duplicate torrent file")
                return True
            self.log.exception(err)
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
