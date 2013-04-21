from os.path import join
from logging import getLogger
from requests import get, RequestException
from tranny.exceptions import InvalidResponse

log = getLogger("tranny.net")


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
    log.debug("Downloading release [{0}]: {1}".format(release_name, url))
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
        log.debug("Fetching url: {0}".format(url))
        response = get(url, auth=auth)
        response.raise_for_status()
        if not response.content:
            raise InvalidResponse("Empty response body")
    except (RequestException, InvalidResponse) as err:
        log.exception(err.message)
    else:
        response = response.content
        if json:
            response = response.json()

    finally:
        return response
