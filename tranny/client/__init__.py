# -*- coding: utf-8 -*-
"""
Base classes and methods shared between torrent client implementations
"""
from __future__ import unicode_literals, absolute_import
from collections import namedtuple
import logging
from tranny import util
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
        """ Fetch optional information about the client, for display purposes only

        :return: Client info
        :rtype: dict
        """
        return {}

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


class ClientTorrentData(dict):
    """
    A struct used to hold data regarding torrent info sent from the backend client in use
    """

    def __init__(self, info_hash, name, ratio, up_rate, dn_rate, up_total, dn_total, size, size_completed,
                 leechers, total_leechers, peers, total_peers, priority, private, is_active, progress, **kwargs):
        super(ClientTorrentData, self).__init__(**kwargs)
        self['info_hash'] = info_hash
        self['name'] = name
        self['ratio'] = util.fmt_ratio(ratio)
        self['up_rate'] = up_rate
        self['dn_rate'] = dn_rate
        self['up_total'] = up_total
        self['dn_total'] = dn_total
        self['size'] = util.file_size(size)
        self['size_completed'] = size_completed
        self['leechers'] = leechers
        self['total_leechers'] = total_leechers
        self['peers'] = peers
        self['total_peers'] = total_peers
        self['priority'] = priority
        self['private'] = private
        self['is_active'] = is_active
        self['progress'] = util.fmt_ratio(progress)


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
        #from tranny.client.utorrent import UTorrentClient as TorrentClient
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
