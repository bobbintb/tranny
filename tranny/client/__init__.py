from ..app import config


class ClientProvider(object):
    def list(self):
        raise NotImplementedError("list is not implemented")

    def add(self, data, download_dir=None):
        raise NotImplementedError("add is not implemented")

    def client_version(self):
        return "No client configured"

    def __str__(self):
        return self.client_version()


def init_client(client_type=None):
    if not client_type:
        client_type = config.get_default("general", "client", "transmission").lower()
    if client_type == "rtorrent":
        from .rtorrent import RTorrentClient as TorrentClient
    elif client_type == "transmission":
        from .transmission import TransmissionClient as TorrentClient
    elif client_type == "utorrent":
        from .utorrent import UTorrentClient as TorrentClient
    else:
        raise client_type("Invalid client type supplied: {0}".format(client_type))
    return TorrentClient()
