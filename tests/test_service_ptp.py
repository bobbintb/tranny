import unittest
from testcase import TrannyTestCase
from tranny.provider import ptp


#@unittest.skipUnless(btn_api, "No API Key set for BTN")
class PTPAPITest(TrannyTestCase):
    def setUp(self):
        self.load_config(self.get_fixture("test_config.ini"))
        self.api = ptp.PTP('service_ptp')

    def test_find_matches(self):
        r = []
        for release in self.api.find_matches():
            r.append(release)
        self.assertEqual(10, len(r))


if __name__ == '__main__':
    unittest.main()
