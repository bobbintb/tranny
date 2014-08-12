# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import socket
import urllib
from tranny.client import ClientTorrentData

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib
from tranny.app import config, logger
from tranny import client

__all__ = ['RTorrentClient']


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
    _config_key = "rtorrent"

    def __init__(self):
        self._server = SCGIServerProxy(config.get(self._config_key, 'uri'))

    def client_version(self):
        client = self._server.system.client_version()
        lib = self._server.system.library_version()
        return "rTorrent {}/{}".format(client, lib)

    def add(self, data, download_dir=None):
        payload = xmlrpclib.Binary(data)
        # Make sure the xml-rpc size limit doesnt overflow
        self._server.set_xmlrpc_size_limit(len(payload.data) * 2)
        return self._server.load_raw_start(payload) == 0

    def current_speeds(self):
        dn = self._server.get_down_rate()
        up = self._server.get_up_rate()
        return client.client_speed(up/1024, dn/1024)

    def _multi(self, *args):
        """ Trivial wrapper to d.multicall using the 'main' view

        :param args: Arguments to pass in
        :type args: list
        """
        return self._server.d.multicall('main', *args)

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
            'd.is_active='
        )
        torrent_data = [ClientTorrentData(*t) for t in torrents]
        return torrent_data

    def torrent_stop(self, torrents):
        for torrent in torrents:
            self._server.d.stop(torrent)
        return {}

    def torrent_start(self, torrents):
        for torrent in torrents:
            self._server.d.start(torrent)
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

            sock.send(request_body)
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

        if self.verbose:
            logger.debug('body:', repr(response_body))

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
