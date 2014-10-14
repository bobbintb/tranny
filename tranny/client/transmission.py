# -*- coding: utf-8 -*-
"""
Transmission support module
"""
from __future__ import unicode_literals
from base64 import b64encode
from collections import defaultdict
import functools
from tranny.app import config, Session
from tranny import client
from tranny.service import geoip
from tranny.torrent import Torrent
from transmissionrpc.utils import get_arguments
from tranny import events

try:
    from transmissionrpc import Client, TransmissionError
    from transmissionrpc.constants import DEFAULT_PORT
except ImportError:
    print("""Please install the transmission python library available at
        "http://pythonhosted.org/transmissionrpc/""")
    raise SystemExit()


class TransmissionClient(client.TorrentClient):
    """ Backend implementation for transmission """

    config_key = "client_transmission"

    _torrent_list_args = None

    def __init__(self, host=None, port=None, user=None, password=None):
        super(TransmissionClient, self).__init__()
        if not host:
            host = config.get_default(self.config_key, "host", "localhost")
        self.host = host
        if not port:
            port = config.get_default(self.config_key, "port", DEFAULT_PORT, int)
        self.port = port
        if not user:
            user = config.get_default(self.config_key, "user", None)
        self.user = user
        if not password:
            password = config.get_default(self.config_key, "password", None)
        self.password = password
        self.client = None
        self.connect()

    def client_version(self):
        version = "{}.{} ({})".format(*self.client.server_version)
        return version

    def connect(self):
        try:
            self.client = Client(address=self.host, port=self.port, user=self.user, password=self.password)
        except TransmissionError as err:
            if err.original.code == 111:
                self.log.error("Failed to connect to transmission-daemon, is it running?")
            elif err.original.code == 113:
                self.log.error("No route to host")
            else:
                self.log.exception("Error connecting to transmission server")
            raise

    def add(self, data, download_dir=None):
        """ Add a torrent to the client

        :param data: Torrent data to load in
        :type data: TorrentData
        :param download_dir: Path on deluge server to store download
        :type download_dir: basestring
        :return: Status of successful load (according to deluge)
        :rtype: bool
        """
        try:
            torrent = Torrent.from_str(data.torrent_data)
            try:
                self.torrent_status(torrent.info_hash)
            except KeyError:
                pass
            else:
                self.log.warn("Tried to load duplicate info hash: {}".format(torrent.info_hash))
                return True
            torrent_data = b64encode(data.torrent_data)
            res = self.client.add_torrent(torrent_data, download_dir=download_dir)
        except TransmissionError as err:
            try:
                msg = err._message
            except AttributeError:
                msg = err.message
            if "duplicate torrent" in msg:
                self.log.warning("Tried to add duplicate torrent file")
                return True
            self.log.exception(err)
            return False

        return res

    torrent_add = add

    def current_speeds(self):
        """ Fetch the speeds from the session instance
        :return: Upload, Download speeds in bytes/s
        :rtype: tuple
        """
        ses = self.client.session_stats()
        return ses.uploadSpeed, ses.downloadSpeed

    def torrent_list(self):
        """ Get a list of currently loaded torrents from the client

        :return:
        :rtype:
        """
        if not self._torrent_list_args:
            self._torrent_list_args = get_arguments('torrent-get', self.client.rpc_version)
            self._torrent_list_args.extend(['seeders', 'peersKnown',
                                            'peersGettingFromUs', 'peersSendingToUs',
                                            'isPrivate'])
        torrents = self.client.get_torrents(arguments=self._torrent_list_args)
        torrent_data = list()
        for torrent in torrents:
            data = client.ClientTorrentData(
                info_hash=torrent.hashString,
                name=torrent.name,
                ratio=torrent.ratio,
                up_rate=torrent.rateUpload,
                dn_rate=torrent.rateDownload,
                up_total=torrent.uploadedEver,
                dn_total=torrent.downloadedEver,
                size=torrent.sizeWhenDone,
                size_completed=torrent.sizeWhenDone-torrent.leftUntilDone,
                # TODO peer values are wrong
                peers=torrent.peersGettingFromUs,
                total_peers=0,
                seeders=torrent.peersSendingToUs,
                total_seeders=0,
                priority=torrent.priority,
                private=torrent.isPrivate,
                state=torrent.status,
                progress=torrent.progress
            )
            torrent_data.append(data)
        return torrent_data

    def torrent_remove(self, torrent_id, remove_data=False):
        """ Remove a torrent from the backend client via its torrentID supplied by the
        torrent daemon

        :param remove_data: Remove the torrent data file as well as .torrent
        :type remove_data: bool
        :param torrent_id: TorrentID provided by transmission
        :type torrent_id: int
        """
        self.client.remove_torrent(torrent_id, delete_data=remove_data)

    def torrent_peers(self, info_hash):
        torrent = self.client.get_torrent(info_hash, arguments=['id', 'hashString', 'peers'])
        peers = []
        session = Session()
        # TODO country code lookup
        for peer in torrent.peers:
            peers.append({
                'client': peer['clientName'],
                'down_speed': peer['rateToClient'],
                'up_speed': peer['rateToPeer'],
                'progress': peer['progress'],
                'ip': peer['address'],
                'country': geoip.find_country_code(session, peer['address'])
            })
        return peers

    def torrent_start(self, info_hash):
        self.client.start_torrent(info_hash)
        return True

    def torrent_pause(self, info_hash):
        self.client.stop(info_hash)
        return True

    def torrent_files(self, info_hash):
        files = []
        file_set = self.client.get_files(info_hash)
        for v in file_set.values():
            for file_info in [f for f in v.values()]:
                files.append(client.ClientFileData(
                    path=file_info['name'],
                    progress=file_info['size'] - file_info['completed'],
                    size=file_info['size'],
                    priority=file_info['priority']
                ))
                break
        return files

    def torrent_speed(self, info_hash):
        speed = self.client.get_torrent(info_hash, arguments=['id', 'hashString', 'rateDownload', 'rateUpload'])
        return speed.rateDownload, speed.rateUpload

    def disconnect(self):
        return True

    def torrent_status(self, info_hash):
        key_map = {
            'info_hash': 'hashString',
            'up_rate': 'rateUpload',
            'dn_rate': 'rateDownload',
            'up_total': 'uploadedEver',
            'dn_total': 'downloadedEver',
            'size': 'totalSize',
            'size_completed': 'percentDone',  # wrong
            'seeders': lambda t: len(t.peers),
            'total_seeders': lambda t: len(t.peers),
            'peers': 'peersConnected',
            'total_peers': lambda t: len(t.peers),
            'priority': 'queue_position',
            'private': 'isPrivate',
            'state': 'status',
            'progress': '',
            'tracker_status': '',
            'next_announce': lambda t: t.trackerStats[0]['nextAnnounceTime'],
            'save_path': 'downloadDir',
            'piece_length': 'pieceSize',
            'num_pieces': 'pieceCount',
            'time_added': 'addedDate',
            'distributed_copies': lambda t: functools.reduce(lambda a,b: a+b, [p['progress'] for p in t.peers], 0),
            'active_time': '',
            #'seeding_time': 'secondsSeeding', Not found in my version? trans 2.8.4
            'num_files': lambda t: len(torrent.files()),
            'queue_position': 'queue_position'
        }
        torrent = self.client.get_torrent(info_hash)
        detail = client.ClientTorrentDataDetail(info_hash=info_hash)
        for key in detail.key_list:
            val = key_map.get(key, None)
            if val:
                if callable(val):
                    detail[key] = val(torrent)
                else:
                    detail[key] = getattr(torrent, val)
        return detail

    def torrent_recheck(self, info_hash):
        self.client.verify_torrent(info_hash)
        return True

    def torrent_reannounce(self, info_hash):
        self.client.reannounce_torrent(info_hash)
        return True

    def torrent_queue_up(self, info_hash):
        self.client.queue_up(info_hash)
        return True

    def torrent_queue_down(self, info_hash):
        self.client.queue_down(info_hash)
        return True

    def torrent_queue_top(self, info_hash):
        self.client.queue_top(info_hash)
        return True

    def torrent_queue_bottom(self, info_hash):
        self.client.queue_bottom(info_hash)
        return True

    def torrent_move_data(self, info_hash, dest):
        self.client.move_torrent_data(info_hash, dest)
        return True
