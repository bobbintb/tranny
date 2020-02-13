# -*- coding: utf-8 -*-

from .testcase import get_fixture, TrannyDBTestCase
from unittest import main
from tranny import net
from tranny.app import Session
from tranny.service import geoip


class GeoIPTest(TrannyDBTestCase):
    tmp_dir = None

    def test_geoip(self):
        session = Session()
        db_file_path = get_fixture("GeoIPCountryCSV.zip")
        self.assertTrue(geoip.update(session, db_file_path))
        self.assertEqual(10, session.query(geoip.models.GeoIP).count())

        self.assertEqual("AU", geoip.find_country_code(session, 16777217))
        self.assertEqual("AU", geoip.find_country_code(session, net.int2ip(16777217)))

        self.assertIsNone(geoip.find_country_code(session, 1000))



if __name__ == '__main__':
    main()

