from os.path import join
from logging import getLogger
from requests import get, RequestException
from tranny.exceptions import InvalidResponse

def download(release_name, url, dest_path="./", extension=".torrent"):
    log = getLogger("tranny.net.download")
    file_path = join(dest_path, release_name) + extension
    dl_ok = False
    try:
        response = get(url)
        response.raise_for_status()
        if not response.content:
            raise InvalidResponse("Empty response body")
    except (RequestException, InvalidResponse) as err:
        log.error(err.message)
    else:
        with open(file_path, 'wb') as torrent_file:
            torrent_file.write(response.content)
        dl_ok = True
    finally:
        return dl_ok


