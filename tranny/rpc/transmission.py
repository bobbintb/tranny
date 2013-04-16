from logging import getLogger

log = getLogger("rpc.transmission")

try:
    from transmissionrpc import Client
    from transmissionrpc.constants import DEFAULT_PORT
except ImportError, err:
    log.error("""Please install the transmission python library available at
        "http://pythonhosted.org/transmissionrpc/""")
    raise SystemExit(err)


class TransmissionClient(object):
    _config_key = "transmisttion"

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
        res = self.client.add(data, download_dir=download_dir)
        return res

    def add_uri(self, uri):
        torrent = self.client.add_uri(uri=uri)
        return torrent

    def info(self, torrent_id):
        torrent_info = self.client.info(torrent_id)
        return torrent_info

    def list(self):
        return self.client.list()

    def remove(self, torrent_id):
        return self.client.remove(torrent_id)
