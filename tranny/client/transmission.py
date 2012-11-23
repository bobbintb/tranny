from transmissionrpc import Client
from transmissionrpc.constants import DEFAULT_PORT

class TransmissionClient(object):
    def __init__(self, host="localhost", port=DEFAULT_PORT):
        self.client = Client(host, port=port, user=None, password=None)

    def add(self, uri):
        torrent = self.client.add_uri(uri=uri)
        return torrent

    def info(self, torrent_id):
        torrent_info = self.client.info(torrent_id)
        return torrent_info

    def list(self):
        return self.client.list()

    def remove(self, torrent_id):
        return self.client.remove(torrent_id)