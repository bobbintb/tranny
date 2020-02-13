# -*- coding: utf-8 -*-
"""

"""

from zipfile import ZipFile
import logging
from os.path import join
import csv
from sqlalchemy import and_
from sqlalchemy.exc import DBAPIError
from tranny import net
from tranny import util
from tranny import models
from tranny import cache
from tranny.app import config

_db_url = 'http://geolite.maxmind.com/download/geoip/database/GeoIPCountryCSV.zip'

log = logging.getLogger(__name__)


def fetch_update(download=True, url=_db_url):
    tmp_dir = join(config.config_path, 'geoip_temp')
    util.mkdirp(tmp_dir)
    tmp_dir_file = join(tmp_dir, 'geolite2.zip')
    if download:
        data_set = net.http_request(url, json=False)
        if data_set:
            with open(tmp_dir_file, 'wb') as out:
                out.write(data_set)
    return tmp_dir_file


def update(session, db_file_path):
    try:
        deleted_rows = session.query(models.GeoIP).delete()
        session.commit()
    except DBAPIError:
        log.exception("Failed to drop old records")
        session.rollback()
    else:
        log.info("Dropped existing data successfully: {} rows".format(deleted_rows))
        with ZipFile(db_file_path) as zip_data:
            f = zip_data.open(zip_data.filelist[0])
            reader = csv.reader(f)
            for line in (l for l in reader if l):
                session.add(models.GeoIP(*line[2:]))
                log.info("Adding: {}:{} [{}]".format(line[2], line[3], line[4]))
        try:
            session.commit()
        except DBAPIError:
            log.exception("Failed to insert new records")
            session.rollback()
        else:
            return True
    return False


@cache.cache_on_arguments(expiration_time=3600*7)
def find_country_code(session, ip_address):
    """ Return the 2 letter country code for the ip address provided

    :param session:
    :type session:
    :param ip_address:
    :type ip_address:
    :return:
    :rtype:
    """
    try:
        ip_int = int(ip_address)
    except ValueError:
        ip_int = net.ip2int(ip_address)
    cn = session.query(models.GeoIP).filter(
        and_(
            models.GeoIP.ip_start <= ip_int,
            models.GeoIP.ip_end >= ip_int)
    ).first()
    if cn:
        return cn.code
    else:
        return 'NA'

