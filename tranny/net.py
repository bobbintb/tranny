# -*- coding: utf-8 -*-
"""
Functions used to download data over HTTP connections
"""

from functools import partial
import logging
import socket
import struct
import gevent
from os.path import join
from requests import RequestException, Session, HTTPError
from tranny import app
from tranny import exceptions

log = logging.getLogger(__name__)

# Conversion table mostly used for converting 3rd party API values into common bytes
speed_multi = {
    # Binary JEDEC keys
    'B': lambda v: v,
    'KB': lambda v: v * 1024,
    'MB': lambda v: v * 1024 ** 2,
    'GB': lambda v: v * 1024 ** 3,
    'TB': lambda v: v * 1024 ** 4,
    'PB': lambda v: v * 1024 ** 5,

    # Binary IEC keys
    'KiB': lambda v: v * 1024,
    'MiB': lambda v: v * 1024 ** 2,
    'GiB': lambda v: v * 1024 ** 3,
    'TiB': lambda v: v * 1024 ** 4,
    'PiB': lambda v: v * 1024 ** 5,

    # Decimal metric keys
    'b': lambda v: v,
    'kb': lambda v: v * 1000,
    'mb': lambda v: v * 1000 ** 2,
    'gb': lambda v: v * 1000 ** 3,
    'tb': lambda v: v * 1000 ** 4,
    'pb': lambda v: v * 1000 ** 5,
}


def download(release_name, url, dest_path="./", extension=".torrent"):
    """ Download a file to a local file path

    :param release_name:
    :type release_name:
    :param url:
    :type url:
    :param dest_path:
    :type dest_path:
    :param extension:
    :type extension:
    :return:
    :rtype:
    """
    log.info("Downloading release [{0}]: {1}".format(release_name, url))
    file_path = join(dest_path, release_name)
    if extension and not file_path.endswith(extension):
        file_path += extension
    dl_ok = False
    response = http_request(url)
    if response:
        with open(file_path, 'wb') as torrent_file:
            torrent_file.write(response.content)
        dl_ok = True
    return dl_ok


def http_request(url, auth=None, json=True, timeout=30, method='get', data=None, params=None):
    """ Fetch and return data contained at the url provided

    :param data:
    :param method:
    :param timeout:
    :param json:
    :param auth:
    :param url: URL to fetch
    :type url: basestring
    :return: HTTP response body
    :rtype: basestring, None
    """
    response = None
    try:
        log.debug("Fetching url: {0}".format(url))
        if method == 'get':
            req = get(url, auth=auth, proxies=app.config.get_proxies(), timeout=timeout, params=params)
        elif method == 'post':
            req = post(url, data=data, auth=auth, proxies=app.config.get_proxies(), timeout=timeout)
        else:
            raise RequestException("Unsupported request method type: {}".format(method))
        req = send(req)
        req.raise_for_status()
        if not req.content:
            raise exceptions.InvalidResponse("Empty response body")
    except (HTTPError, RequestException, exceptions.InvalidResponse) as err:
        log.exception(err.message)
        response = {}
    else:
        if json:
            response = req.json()
        else:
            response = req.content
    finally:
        return response


def parse_net_speed_value(input_speed):
    """ Convert a string like 10 kb/s into a byte count

    :param input_speed: Net speed string with suffix
    :type input_speed: unicode
    :return: Speed in bytes
    :rtype: int
    """
    value, suffix = input_speed.replace("/s", "").split()
    parsed_value = float(speed_multi[suffix](float(value)))
    return parsed_value


def ip2int(addr):
    """ Convert an ip address into its int form

    :param addr: quad dotted ip address
    :type addr: unicdoe
    :return: Integer IP
    :rtype: int
    """
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
    """ Convert an integer into an ip form ip

    :param addr:
    :type addr:
    :return:
    :rtype:
    """
    return socket.inet_ntoa(struct.pack("!I", addr))


class AsyncRequest(object):
    """ Asynchronous request.

    Accept same parameters as ``Session.request`` and some additional:

    :param session: Session which will do request
    :param callback: Callback called on response.
                     Same as passing ``hooks={'response': callback}``
    """
    def __init__(self, method, url, **kwargs):
        #: Request method
        self.method = method
        #: URL to request
        self.url = url
        #: Associated ``Session``
        self.session = kwargs.pop('session', None)
        if self.session is None:
            self.session = Session()

        callback = kwargs.pop('callback', None)
        if callback:
            kwargs['hooks'] = {'response': callback}

        #: The rest arguments for ``Session.request``
        self.kwargs = kwargs
        #: Resulting ``Response``
        self.response = None

    def send(self, **kwargs):
        """
        Prepares request based on parameter passed to constructor and optional ``kwargs```.
        Then sends request and saves response to :attr:`response`

        :returns: ``Response``
        """
        merged_kwargs = {}
        merged_kwargs.update(self.kwargs)
        merged_kwargs.update(kwargs)
        try:
            self.response = self.session.request(self.method,
                                                self.url, **merged_kwargs)
        except Exception as e:
            self.exception = e
        return self.response


def send(r, pool=None, stream=False):
    """Sends the request object usingN the specified pool. If a pool isn't
    specified this method blocks. Pools are useful because you can specify size
    and can hence limit concurrency."""
    if pool is not None:
        return pool.spawn(r.send, stream=stream)

    return gevent.spawn(r.send, stream=stream).get(block=True)

get = partial(AsyncRequest, 'GET')
post = partial(AsyncRequest, 'POST')
