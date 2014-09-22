# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import os.path
import re
import socket
import urllib
import logging
import shutil

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib
from tranny.app import config
from tranny import client
from tranny.torrent import Torrent

__all__ = ['RTorrentClient']

log = logging.getLogger(__name__)

class RTorrentClient(client.TorrentClient):
    """ rTorrent client support module. This class will talk to rtorrent over its
    scgi+xmlrpc API interface. (Why not just xml-rpc?, arg..). This means that
    you do NOT have to use a SCGI webserver to facilitate the requests. The client
    speaks SCGI directly. In the future i will probably add a more standard client
    using a webserver for the added security mechanisms it adds for a remote
    connection. Right now you can allow access to the ip:port directly but you
    are **strongly** advised to at least add a firewall rule to only allow
    your own IP to connect.

    rtorrent must be configured similar to this:

    scgi_port = localhost:5000

    """
    config_key = "client_rtorrent"

    def __init__(self, uri):
        self._server = SCGIServerProxy(uri)

    def client_version(self):
        client = self._server.system.client_version()
        lib = self._server.system.library_version()
        return "rTorrent {}/{}".format(client, lib)

    def add(self, torrent, download_dir=None):
        payload = xmlrpclib.Binary(torrent.torrent_data)
        info_hash = Torrent.from_str(torrent.torrent_data).info_hash.upper()
        # Make sure the xml-rpc size limit doesnt overflow
        self._server.set_xmlrpc_size_limit(len(torrent.torrent_data) * 2)
        self._server.load_raw(payload)
        if download_dir:
            self._server.d.set_directory_base(info_hash, download_dir)
        self._server.d.start(info_hash)
        return True

    def current_speeds(self):
        dn = self._server.get_down_rate()
        up = self._server.get_up_rate()
        return client.client_speed(up, dn)

    def _multi(self, *args, **kwargs):
        """ Trivial wrapper to d.multicall, defaulting to the 'main' view

        :param args: Arguments to pass in
        :type args: list
        """
        if 'view' in kwargs.keys():
            view = kwargs['view']
        else:
            view = 'main'
        return self._server.d.multicall(view, *args)

    def torrent_list(self):
        torrents = self._multi(
            'd.hash=',
            'd.get_name=',
            'd.get_ratio=',
            'd.get_up_rate=',
            'd.get_down_rate=',
            'd.get_up_total=',
            'd.get_down_total=',
            'd.get_size_bytes=',
            'd.get_completed_bytes=',
            'd.get_peers_accounted=',
            'd.get_peers_complete=',
            'd.get_priority=',
            'd.is_private=',
            'd.is_active=',
            'd.is_hash_checking=',
            'd.is_open=',
            'd.get_complete=',
            'd.get_message='
        )
        # Missing fields: seeders, total seederss
        torrent_array = []
        for t in torrents:
            tdata = client.ClientTorrentData(
                seeders = '0',
                total_seeders = '0'
            )
            # Do all the easy stuff first
            tdata.update(dict(zip([
                'info_hash',
                'name',
                'ratio',
                'up_rate',
                'dn_rate',
                'up_total',
                'dn_total',
                'size',
                'size_completed',
                'peers',
                'total_peers',
                'priority',
                'private'
            ], t[:13])))

            if t[17]:
                tdata['state'] = 'Error'
            elif t[14]:
                tdata['state'] = 'Hashing'
            elif not t[15]:
                tdata['state'] = 'Closed'
            elif not t[13]:
                tdata['state'] = 'Paused'
            elif t[16]:
                tdata['state'] = 'Seeding'
            elif not t[16]:
                tdata['state'] = 'Leeching'
            else:
                tdata['state'] = 'Unknown'

            tdata['progress'] = (float(t[8]) / t[7]) * 100
            
            torrent_array.append(tdata)
        return torrent_array

    def torrent_speed(self, info_hash):
        return {'upload_payload_rate': self._server.d.get_down_rate(info_hash),
                'download_payload_rate': self._server.d.get_up_rate(info_hash)}

    def torrent_status(self, info_hash):
        status_map = {
            'dn_total': 'd.get_down_total',
            'up_total': 'd.get_up_total',
            'ratio': 'd.get_ratio',
            'name': 'd.name',
            'save_path': 'd.get_directory_base',
            'size': 'd.get_size_bytes',
            'piece_length': 'd.get_chunk_size',
            'num_pieces': 'd.size_chunks',
            'peers': 'd.get_peers_connected',
            'dn_rate': 'd.get_down_rate',
            'up_rate': 'd.get_up_rate',
        }
        # Predefine unimplmented items here
        data = client.ClientTorrentDataDetail(**{
            'info_hash': info_hash,
            'next_announce': 'N/A',
            'tracker_status': 'N/A',
            'seeders': '0',
            'total_seeders': '0',
            'total_peers': '0',
            'distributed_copies': 'N/A',
            'time_added': '1970-01-01',
            'active_time': '0',
            'seeding_time': '0',
            'eta': 0
        })
        for field, call in status_map.items():
            data[field] = getattr(self._server, call)(info_hash)
        return data

    def torrent_peers(self, info_hash):
        data_mapping = {
            'client': 'p.get_client_version=',
            'down_speed': 'p.get_down_rate=',
            'progress': 'p.completed_percent=',
            'ip': 'p.address=',
            'up_speed': 'p.get_up_rate=',
        }
        parray = self._server.p.multicall(info_hash, '+0', *data_mapping.values())
        pdata = []
        for peer in parray:
            # Country data not implemented yet
            peer_dict = client.ClientPeerData({'country': 'CA'})
            for index, value in enumerate(data_mapping.keys()):
                peer_dict[value] = peer[index]
            pdata.append(peer_dict)
        return pdata

    def torrent_files(self, info_hash):
        files = self._server.f.multicall(info_hash, '+0', 'f.get_path=', 'f.get_size_bytes=', 'f.get_size_chunks=', 'f.get_completed_chunks=', 'f.get_priority=')
        file_data = []
        for f in files:
            file_data.append(client.ClientFileData(
                path = f[0],
                size = f[1],
                priority = f[4],
                progress = (float(f[3])/f[2])*100
            ))

        

    def torrent_remove(self, info_hash, remove_data=False):
        if remove_data:
            # Release the files first
            self._server.d.close(info_hash)
            if self._server.d.is_multi_file(info_hash):
                for f in self._server.f.multicall(info_hash, 0, 'f.get_frozen_path='):
                    if os.path.isdir(f[0]):
                        shutil.rmtree(f[0])
                    elif os.path.isfile(f[0]):
                        os.unlink(f[0])
                shutil.rmtree(self._server.d.get_base_path(info_hash))
            else:
                os.unlink(self._server.d.get_base_path(info_hash))
        self._server.d.erase(info_hash)

    def torrent_reannounce(self, info_hash):
        for info_hash in info_hash:
            self._server.d.tracker_announce(info_hash)

    def torrent_pause(self, torrents):
        for info_hash in torrents:
            self._server.d.stop(info_hash)

    def torrent_stop(self, torrents):
        for info_hash in torrents:
            self._server.d.close(info_hash)

    def torrent_start(self, torrents):
        for info_hash in torrents:
            self._server.d.start(info_hash)

    def torrent_recheck(self, torrents):
        for info_hash in torrents:
            self._server.d.check_hash(info_hash)

    def get_capabilities(self):
        return ['torrent_add', 'torrent_list']

    def get_events(self):
        # Wouldn't be impossible to implement in the future
        return {}

class SCGITransport(xmlrpclib.Transport):
    def single_request(self, host, handler, request_body, verbose=0):
        # Add SCGI headers to the request.
        headers = {'CONTENT_LENGTH': str(len(request_body)), 'SCGI': '1'}
        header = '\x00'.join(('%s\x00%s' % item for item in headers.items())) + '\x00'
        header = '%d:%s' % (len(header), header)
        request_body = '%s,%s' % (header, request_body)
        sock = None
        try:
            if host:
                host, port = urllib.splitport(host)
                addrinfo = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
                sock = socket.socket(*addrinfo[0][:3])
                sock.connect(addrinfo[0][4])
            else:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(handler)

            self.verbose = verbose

            sock.sendall(request_body)
            return self.parse_response(sock.makefile())
        finally:
            if sock:
                sock.close()

    def parse_response(self, response):
        p, u = self.getparser()

        response_body = ''
        while True:
            data = response.read(1024)
            if not data:
                break
            response_body += data

        # Remove SCGI headers from the response.
        response_header, response_body = re.split(r'\n\s*?\n', response_body, maxsplit=1)

        p.feed(response_body)
        p.close()

        return u.close()


class SCGIServerProxy(xmlrpclib.ServerProxy):
    def __init__(self, uri, transport=None, encoding=None, verbose=False, allow_none=False, use_datetime=False):
        uri_type, uri = urllib.splittype(uri)
        if not uri_type == 'scgi':
            raise IOError('unsupported XML-RPC protocol')
        self.__host, self.__handler = urllib.splithost(uri)
        if not self.__handler:
            self.__handler = '/'

        if transport is None:
            transport = SCGITransport(use_datetime=use_datetime)
        self.__transport = transport

        self.__encoding = encoding
        self.__verbose = verbose
        self.__allow_none = allow_none

    def __close(self):
        self.__transport.close()

    def __request(self, method_name, params):
        # call a method on the remote server

        request = xmlrpclib.dumps(params, method_name, encoding=self.__encoding, allow_none=self.__allow_none)
        response = self.__transport.request(self.__host, self.__handler, request, verbose=self.__verbose)
        if len(response) == 1:
            response = response[0]
        return response

    def __repr__(self):
        return "<SCGIServerProxy for {}{}>".format(self.__host, self.__handler)

    __str__ = __repr__

    def __getattr__(self, name):
        # magic method dispatcher
        return xmlrpclib._Method(self.__request, name)

    # note: to call a remote object with an non-standard name, use
    # result getattr(server, "strange-python-name")(args)

    def __call__(self, attr):
        """A workaround to get special attributes on the ServerProxy
           without interfering with the magic __getattr__
        """
        if attr == "close":
            return self.__close
        elif attr == "transport":
            return self.__transport
        raise AttributeError("Attribute %r not found" % (attr,))
