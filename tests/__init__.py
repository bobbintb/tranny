import unittest
from os.path import join, dirname
from tranny import init_config

main = unittest.main


class TrannyTestCase(unittest.TestCase):
    def get_config(self, fixture_name="test_config.ini"):
        return init_config(get_fixture(fixture_name))


def get_fixture(fixture_file):
    return join(dirname(__file__), "fixtures", fixture_file)
