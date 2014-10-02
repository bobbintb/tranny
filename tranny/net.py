# -*- coding: utf-8 -*-
"""
Functions used to download data over HTTP connections
"""
from __future__ import unicode_literals, absolute_import
import logging
import socket
import struct
from os.path import join
from requests import get, RequestException, post
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
            response = get(url, auth=auth, proxies=app.config.get_proxies(), timeout=timeout, params=params)
        elif method == 'post':
            response = post(url, data=data, auth=auth, proxies=app.config.get_proxies(), timeout=timeout)
        response.raise_for_status()
        if not response.content:
            raise exceptions.InvalidResponse("Empty response body")
    except (RequestException, exceptions.InvalidResponse) as err:
        log.exception(err.message)
        response = {}
    else:
        if json:
            response = response.json()
        else:
            response = response.content
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
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))
