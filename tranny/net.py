# -*- coding: utf-8 -*-
"""
Functions used to download data over HTTP connections
"""
from __future__ import unicode_literals
from os.path import join
from requests import get, RequestException
from tranny import app, exceptions


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


def fetch_url(url, auth=None, json=True):
    """ Fetch and return data contained at the url provided

    :param url: URL to fetch
    :type url: basestring
    :return: HTTP response body
    :rtype: basestring, None
    """
    response = None
    try:
        app.logger.debug("Fetching url: {0}".format(url))
        response = get(url, auth=auth, proxies=app.config.get_proxies())
        response.raise_for_status()
        if not response.content:
            raise exceptions.InvalidResponse("Empty response body")
    except (RequestException, exceptions.InvalidResponse) as err:
        app.logger.exception(err.message)
    else:
        response = response.content
        if json:
            response = response.json()
    finally:
        return response
