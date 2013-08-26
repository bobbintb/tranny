import unittest
from os.path import join, dirname
from tranny.app import config

main = unittest.main


class TrannyTestCase(unittest.TestCase):
    @staticmethod
    def get_config(fixture_name="test_config.ini"):
        return config.read(get_fixture(fixture_name))

    def run_data_set(self, test_data, fn):
        for expected, data in test_data:
            self.assertEqual(expected, fn(data), data)


def get_fixture(fixture_file):
    return join(dirname(__file__), "fixtures", fixture_file)
