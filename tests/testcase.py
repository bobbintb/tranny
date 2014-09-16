# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, absolute_import, with_statement
import unittest
from os.path import join, dirname
from sqlalchemy import create_engine
from tranny.app import config, Session, Base

class TrannyTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(TrannyTestCase, self).__init__(methodName=methodName)
        self.load_config()
        self.init_db()

    def load_config(self, config_name="test_config.ini"):
        conf_file = self.get_fixture(config_name)
        ok = 1 == len(config.initialize(conf_file))
        return ok

    def get_config(self):
        return config

    def run_data_set(self, test_data, fn):
        for expected, data in test_data:
            self.assertEqual(expected, fn(data), data)

    def get_fixture(self, fixture_file):
        file_path = join(dirname(__file__), "fixtures", fixture_file)
        return file_path


class TrannyDBTestCase(TrannyTestCase):
    def __init__(self, methodName='runTest'):
        super(TrannyDBTestCase, self).__init__(methodName=methodName)
        self.init_db()

    def init_db(self, uri="sqlite://"):
        Session.remove()
        engine = create_engine(uri)
        Session.configure(bind=engine)
        Base.metadata.create_all(bind=engine)
