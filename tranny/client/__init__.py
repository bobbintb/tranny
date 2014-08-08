# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from collections import namedtuple
from tranny.app import config
from tranny.exceptions import ConfigError

client_speed = namedtuple('client_speed', ['up', 'dn'])


class ClientProvider(object):
    """
    Base class to provide a interface for interacting with backend torrent
    clients.
    """
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

    def current_speeds(self):
        """ Fetch a tuple of the current upload and download speeds in the client

        :return: Upload and download speed in kbps
        :rtype: tuple
        """
        return client_speed(0.0, 0.0)

    def torrent_list(self):
        raise NotImplementedError('torrent_list undefined')


class ClientTorrentData(dict):
    """
    A struct used to hold data regarding torrent info sent from the backend client in use
    """

    def __init__(self, info_hash, name, ratio, up_rate, dn_rate, up_total, dn_total, size_total, size_completed,
                 leechers, peers, priority, private, is_active, **kwargs):
        super(ClientTorrentData, self).__init__(**kwargs)
        self['DT_RowId'] = info_hash
        self['info_hash'] = info_hash
        self['name'] = name
        self['ratio'] = ratio
        self['up_rate'] = up_rate
        self['dn_rate'] = dn_rate
        self['up_total'] = up_total
        self['dn_total'] = dn_total
        self['size_total'] = size_total
        self['size_completed'] = size_completed
        self['leechers'] = leechers
        self['peers'] = peers
        self['priority'] = priority
        self['private'] = private
        self['is_active'] = is_active


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
        from tranny.client.rtorrent import RTorrentClient as TorrentClient
    elif client_type == "transmission":
        from tranny.client.transmission import TransmissionClient as TorrentClient
    elif client_type == "utorrent":
        from tranny.client.utorrent import UTorrentClient as TorrentClient
    elif client_type == "deluge":
        from tranny.client.deluge import DelugeJSONRPCClient as TorrentClient
    else:
        raise ConfigError("Invalid client type supplied: {0}".format(client_type))
    return TorrentClient()
