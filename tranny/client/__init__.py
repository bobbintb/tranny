# -*- coding: utf-8 -*-
"""
Base classes and methods shared between torrent client implementations
"""
from __future__ import unicode_literals, absolute_import
from abc import ABCMeta, abstractmethod
from collections import namedtuple, defaultdict
import logging
from tranny import app
from tranny.app import config
from tranny.exceptions import ConfigError
from tranny import events
from tranny.plugin import BasePlugin
from tranny import api

client_speed = namedtuple('client_speed', ['up', 'dn'])


class TorrentState(object):
    STARTED = 'started'
    STOPPED = 'stopped'
    PAUSED = STOPPED
    CHECKING = 'checking'
    DOWNLOADING = 'downloading'


class TorrentClient(BasePlugin):
    """
    Base class to provide a interface for interacting with backend torrent
    clients.
    """

    __metaclass__ = ABCMeta

    config_key = 'undefined'

    def __init__(self):
        super(TorrentClient, self).__init__(self.config_key)
        self.connected = False
        self.log = logging.getLogger(__name__)
        self._last_state = {}
        self._last_update = 0

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

    @abstractmethod
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

    @abstractmethod
    def current_speeds(self):
        """ Fetch a tuple of the current upload and download speeds in the client

        :return: Upload and download speed in kbps
        :rtype: tuple
        """
        return client_speed(0.0, 0.0)

    @abstractmethod
    def torrent_list(self):
        raise NotImplementedError('torrent_list undefined')

    @abstractmethod
    def torrent_status(self, info_hash):
        raise NotImplementedError("torrent_status undefined")

    @abstractmethod
    def torrent_pause(self, info_hash):
        raise NotImplementedError("torrent_pause undefined")

    @abstractmethod
    def torrent_start(self, info_hash):
        raise NotImplementedError("torrent_start undefined")

    @abstractmethod
    def torrent_remove(self, info_hash):
        raise NotImplementedError("torrent_remove undefined")

    @abstractmethod
    def torrent_reannounce(self, info_hash):
        raise NotImplementedError("torrent_reannounce undefined")

    @abstractmethod
    def torrent_recheck(self, info_hash):
        raise NotImplementedError("torrent_recheck undefined")

    @abstractmethod
    def torrent_files(self, info_hash):
        raise NotImplementedError("torrent_files undefined")

    @abstractmethod
    def torrent_add(self, torrent):
        raise NotImplementedError("torrent_add undefined")

    @abstractmethod
    def torrent_peers(self, info_hash):
        raise NotImplementedError("torrent_peers undefined")

    @abstractmethod
    def torrent_queue_up(self, info_hash):
        pass

    @abstractmethod
    def torrent_queue_down(self, info_hash):
        pass

    @abstractmethod
    def torrent_queue_top(self, info_hash):
        pass

    @abstractmethod
    def torrent_queue_bottom(self, info_hash):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    def get_handlers(self):
        return [
            events.EventHandler(events.EVENT_TICK_5, self.update)
        ]

    def get_events(self):
        new_events = defaultdict(list)
        new_torrents = {t.info_hash: t for t in self.torrent_list()}
        if not self._last_state:
            self._last_state = new_torrents
            return new_events
        known_hashes = {t.info_hash for k, t in self._last_state.items()}
        for torrent in self._last_state.values():
            if torrent.info_hash not in known_hashes:
                # Torrent not in old, must be new
                new_events[events.EVENT_TORRENT_NEW].append(torrent)
                continue
            if not torrent.info_hash in new_torrents:
                # Torrent not in new list, must be removed
                new_events[events.EVENT_TORRENT_REMOVE].append(torrent)
                continue
            # Generate a diff of certain keys
            updates = torrent.changes(self._last_state[torrent.info_hash],
                                      ['ratio', 'up_rate', 'dn_rate', 'up_total', 'dn_total',
                                       'size_completed', 'peers', 'total_peers', 'seeders',
                                       'total_seeders', 'priority'])
            if updates:
                new_events[events.EVENT_TORRENT_UPDATE].append(updates)
        self._last_state = new_torrents
        return new_events

    def update(self, payload=None):
        """
        Update tick handler registered as a plugin
        """
        self.log.debug("Fetching new torrent events")
        new_event = self.get_events()
        for k, v in new_event.items():
            self.log.debug("[{}] {}".format(k, v))
        if new_event:
            api.emit(events.EVENT_TORRENT_UPDATE, data=new_event)
        return payload

    @abstractmethod
    def torrent_move_data(self, info_hash, dest):
        pass


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

    def __unicode__(self):
        return "{} [{}]".format(self['info_hash'], self['name'])

    def __str__(self):
        return self.__unicode__().encode("utf-8")

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise

    def __setattr__(self, name, value):
        if name in self:
            self[name] = value
        else:
            raise AttributeError("Invalid property name: {}".format(name))

    @property
    def key_list(self):
        """ Returns the list of valid keys

        :return: Struct keys
        :rtype: []unicode
        """
        return self._keys

    def changes(self, old, valid_keys=None):
        changes = {}
        if not valid_keys:
            valid_keys = self.keys()
        for key, new_value in self.items():
            if not key in valid_keys:
                continue
            if not old[key] == new_value:
                changes[key] = new_value
        return changes


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
        'comment',
        'queue_position'
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

    client = Client(**config_values)
    from tranny.app import plugin_manager
    plugin_manager.register(client)

    return client


def get():
    """ Return a reference to the current torrent client in use

    TODO remove references to this as its no longer needed

    .. deprecated:: 0.1
        Use the app.torrent_client reference directly

    :return: Current torrent client backend in use
    :rtype: tranny.client.TorrentClient()
    """
    return app.torrent_client
