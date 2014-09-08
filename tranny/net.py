# -*- coding: utf-8 -*-
"""
Functions used to download data over HTTP connections
"""
from __future__ import unicode_literals
from os.path import join
from requests import get, RequestException
from tranny import app, exceptions

# Conversion table mostly used for converting API values into common bytes
speed_multi = {
    # Binary JEDEC keys
    'KB': lambda v: v * 1024,
    'MB': lambda v: v * 1024 * 1024,
    'GB': lambda v: v * 1024 * 1024 * 1024,
    'TB': lambda v: v * 1024 * 1024 * 1024 * 1024,
    'PB': lambda v: v * 1024 * 1024 * 1024 * 1024 * 1024,

    # Binary IEC keys
    'KiB': lambda v: v * 1024,
    'MiB': lambda v: v * 1024 * 1024,
    'GiB': lambda v: v * 1024 * 1024 * 1024,
    'TiB': lambda v: v * 1024 * 1024 * 1024 * 1024,
    'PiB': lambda v: v * 1024 * 1024 * 1024 * 1024 * 1024,

    # Decimal metric keys
    'kb': lambda v: v * 1000,
    'mb': lambda v: v * 1000 * 1000,
    'gb': lambda v: v * 1000 * 1000 * 1000,
    'tb': lambda v: v * 1000 * 1000 * 1000 * 1000,
    'pb': lambda v: v * 1000 * 1000 * 1000 * 1000 * 1000,
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
    app.logger.info("Downloading release [{0}]: {1}".format(release_name, url))
    file_path = join(dest_path, release_name) + extension
    dl_ok = False
    response = fetch_url(url)
    if response:
        with open(file_path, 'wb') as torrent_file:
            torrent_file.write(response)
        dl_ok = True
    return dl_ok


def fetch_url(url, auth=None, json=True, timeout=10):
    """ Fetch and return data contained at the url provided

    :param url: URL to fetch
    :type url: basestring
    :return: HTTP response body
    :rtype: basestring, None
    """
    response = None
    try:
        app.logger.debug("Fetching url: {0}".format(url))
        response = get(url, auth=auth, proxies=app.config.get_proxies(), timeout=timeout)
        response.raise_for_status()
        if not response.content:
            raise exceptions.InvalidResponse("Empty response body")
    except (RequestException, exceptions.InvalidResponse) as err:
        app.logger.exception(err.message)
        response = {}
    else:
        if json:
            response = response.json()
        else:
            response = response.content
    finally:
        return response


def parse_net_speed_value(input_speed):
    value, suffix = input_speed.replace("/s", "").split()
    parsed_value = float(speed_multi[suffix](float(value)))
    return parsed_value
