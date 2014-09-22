# -*- coding: utf-8 -*-
"""
Base classes and methods shared between torrent client implementations
"""
from __future__ import unicode_literals, absolute_import
from collections import namedtuple
import logging
from tranny import app
from tranny.app import config
from tranny.exceptions import ConfigError

client_speed = namedtuple('client_speed', ['up', 'dn'])


class TorrentClient(object):
    """
    Base class to provide a interface for interacting with backend torrent
    clients.
    """

    config_key = 'undefined'

    def __init__(self):
        self.connected = False
        self.log = logging.getLogger(__name__)

    def list(self):
        """ Retrieve a list of torrents loaded in the client. This list includes all
        torrents, meaning started/stopped/paused/leeching.

        :return: Loaded torrent list
        :rtype: []dict
        """
        raise NotImplementedError("list is not implemented")

    def add(self, data, download_dir=None):
        """ Upload a new torrent to the backend client.

        :param data:
        :type data:
        :param download_dir:
        :type download_dir:
        :return:
        :rtype:
        """
        raise NotImplementedError("add is not implemented")

    def client_version(self):
        """ Fetch and return the client version if available

        :return: Client version
        :rtype: unicode
        """
        return self.__class__.__name__

    def __str__(self):
        return self.client_version()

    def client_information(self):
        """ Fetch information about the client, for display purposes only

        :return: Client info
        :rtype: dict
        """
        return {'Version': self.client_version()}

    def current_speeds(self):
        """ Fetch a tuple of the current upload and download speeds in the client

        :return: Upload and download speed in kbps
        :rtype: tuple
        """
        return client_speed(0.0, 0.0)

    def torrent_list(self):
        raise NotImplementedError('torrent_list undefined')

    def torrent_status(self, info_hash):
        raise NotImplementedError("torrent_status undefined")

    def torrent_pause(self, info_hash):
        raise NotImplementedError("torrent_pause undefined")

    def torrent_start(self, info_hash):
        raise NotImplementedError("torrent_start undefined")

    def torrent_remove(self, info_hash):
        raise NotImplementedError("torrent_remove undefined")

    def torrent_reannounce(self, info_hash):
        raise NotImplementedError("torrent_reannounce undefined")

    def torrent_recheck(self, info_hash):
        raise NotImplementedError("torrent_recheck undefined")

    def torrent_files(self, info_hash):
        raise NotImplementedError("torrent_files undefined")

    def torrent_add(self, torrent):
        raise NotImplementedError("torrent_add undefined")

    def torrent_priority(self, torrent):
        raise NotImplementedError("torrent_priority undefined")

    def torrent_peers(self, info_hash):
        raise NotImplementedError("torrent_peers undefined")

    def disconnect(self):
        raise NotImplementedError("disconnect undefined")

    def get_events(self):
        raise NotImplementedError("get_events undefined")


class ClientDataStruct(dict):
    """
    A base class for any data structures that will be returned by clients
    """
    _keys = []

    def __init__(self, **kwargs):
        for key in self._keys:
            self[key] = None
        super(ClientDataStruct, self).__init__(**kwargs)

    def __getitem__(self, key):
        if key not in self._keys:
            raise KeyError("'" + key + "'" + " is not a valid key")
        return super(ClientDataStruct, self).__getitem__(key)

    def __setitem__(self, key, value):
        if key not in self._keys:
            raise KeyError("'" + key + "'" + " is not a valid key")
        super(ClientDataStruct, self).__setitem__(key, value)

    def is_complete(self):
        """Test if all keys have a value, even if that value is empty, e.g. {}"""
        return all(self.get(key, None) is not None for key in self._keys)


class ClientPeerData(ClientDataStruct):
    """
    A structure to hold peer data from the client
    """
    _keys = [
        'client',
        'down_speed',
        'up_speed',
        'progress',
        'ip',
        'country'
    ]


class ClientTorrentData(ClientDataStruct):
    """
    A struct used to hold data regarding torrent info sent from the backend client in use
    """
    _keys = [
        'info_hash',
        'name',
        'ratio',
        'up_rate',
        'dn_rate',
        'up_total',
        'dn_total',
        'size',
        'size_completed',
        'seeders',
        'total_seeders',
        'peers',
        'total_peers',
        'priority',
        'private',
        'state',
        'progress',
    ]


class ClientTorrentDataDetail(ClientDataStruct):
    """
    A struct to hold more in depth information about a torrent
    """
    _keys = [
        'info_hash',
        'name',
        'ratio',
        'up_rate',
        'dn_rate',
        'up_total',
        'dn_total',
        'size',
        'size_completed',
        'eta',
        'seeders',
        'total_seeders',
        'peers',
        'total_peers',
        'priority',
        'private',
        'state',
        'progress',
        'tracker_status',
        'next_announce',
        'save_path',
        'piece_length',
        'num_pieces',
        'time_added',
        'distributed_copies',
        'active_time',
        'seeding_time',
        'num_files',
        'comment'
    ]


class ClientFileData(ClientDataStruct):
    """
    A struct to hold information about the files inside a torrent
    """
    _keys = [
        'path',
        'size',
        'priority',
        'progress'
    ]


def init_client(client_type=None):
    """ Import & initialize the client set in the configuration file and return the
    usable instance.

    :param client_type: Manually specify a client to load
    :type client_type: unicode
    :return: Configured backend torrent instance
    :rtype: ClientProvider
    """
    if not client_type:
        client_type = config.get_default("general", "client", "transmission").lower()
    if client_type == "rtorrent":
        from tranny.client.rtorrent import RTorrentClient as Client
    elif client_type == "transmission":
        from tranny.client.transmission import TransmissionClient as Client
    elif client_type == "utorrent":
        # from tranny.client.utorrent import UTorrentClient as TorrentClient
        raise NotImplementedError("Utorrent support is currently incomplete. Please use another client")
    elif client_type == "deluge":
        from tranny.client.deluge import DelugeClient as Client
    elif client_type == "simplefile":
        from tranny.client.simplefile import SimpleFileClient as Client
    else:
        raise ConfigError("Invalid client type supplied: {0}".format(client_type))
    config_values = config.get_section_values(Client.config_key)

    return Client(**config_values)


def get():
    """ Return a reference to the current torrent client in use

    TODO remove references to this as its no longer needed

    .. deprecated:: 0.1
        Use the app.torrent_client reference directly

    :return: Current torrent client backend in use
    :rtype: tranny.client.TorrentClient()
    """
    return app.torrent_client
