# -*- coding: utf-8 -*-
"""

"""

import requests
import hashlib
import zipfile
from six import StringIO

#URL = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-Country-CSV.zip'
URL = 'http://ppdm.org/GeoLite2-Country-CSV.zip'
URL_MD5 = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-Country-CSV.zip.md5'


def fetch_database():
    raw_db_zip = requests.get(URL).content
    geoip_db = StringIO(raw_db_zip)
    valid_md5 = requests.get(URL_MD5).content
    fetched_md5 = hashlib.md5(raw_db_zip).hexdigest()
    if not valid_md5 == fetched_md5:
        raise AssertionError("Mismatched MD5")
    zf = zipfile.ZipFile(geoip_db)
    file_set = {name: zf.read(name) for name in zf.namelist()}
    return file_set

if __name__ == "__main__":
    files = fetch_database()
    print((len(files)))
