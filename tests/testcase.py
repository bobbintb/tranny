# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, absolute_import, with_statement
import unittest
from os.path import join, dirname
from tranny.app import config


class TrannyTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(TrannyTestCase, self).__init__(methodName=methodName)
        self.load_config()

    def load_config(self, config_name="test_config.ini"):
        ok = 1 == len(config.read(self.get_fixture(config_name)))
        return ok

    def get_config(self, ):
        return config

    def run_data_set(self, test_data, fn):
        for expected, data in test_data:
            self.assertEqual(expected, fn(data), data)

    def get_fixture(self, fixture_file):
        return join(dirname(__file__), "fixtures", fixture_file)
