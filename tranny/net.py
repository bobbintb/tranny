from os.path import join
from urllib2 import Request, urlopen, HTTPError, URLError
from httplib import HTTPException
from logging import getLogger

def download(release_name, url, dest_path="./", extension=".torrent"):
    log = getLogger("tranny.net.download")
    file_path = join(dest_path, release_name) + extension

    request = Request(url, headers={ 'User-Agent' : 'Tranny/0.1' })
    dl_ok = False
    try:
        response = urlopen(request)
    except (HTTPError, URLError, HTTPException) as err:
        log.error('HTTPError = ' + err.message)
    except Exception as err:
        import traceback
        log.error('Uncaught Exception: ' + traceback.format_exc())
    else:
        torrent_data = response.read()
        with open(file_path, 'wb') as torrent_file:
            torrent_file.write(torrent_data)
        dl_ok = True
    finally:
        return dl_ok


