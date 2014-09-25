# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, absolute_import, with_statement
import unittest
# This env var tells the config loader to use the special test config located at:
# $project_root/tests/fixtures/test_config.ini
# This file must be created from the example config (test_config_dist.ini) in the same
# directory
import os
os.environ['TEST'] = "1"
import pickle
from os.path import join, dirname
from sqlalchemy import create_engine
from tranny.app import config, Session, Base
from tranny.configuration import Configuration
import vcr


def get_fixture(fixture_file):
    return join(dirname(__file__), "fixtures", fixture_file)


class Pickler(object):
    """
    Pickled based serializer
    """
    def serialize(self, obj):
        return pickle.dumps(obj)

    def deserialize(self, s):
        return pickle.loads(s)

tapedeck = vcr.VCR(
    serializer='pickle',
    cassette_library_dir=get_fixture('cassettes'),
)
tapedeck.register_serializer('pickle', Pickler())


def _make_config():
    c = Configuration()
    config_file = get_fixture("test_config.ini")
    c.initialize(config_file)
    return c


class TrannyTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(TrannyTestCase, self).__init__(methodName=methodName)
        config.initialize()

    def run_data_set(self, test_data, fn):
        for expected, data in test_data:
            self.assertEqual(expected, fn(data), data)

    def track(self, track_name):
        return track_name + ".pickle"

class TrannyDBTestCase(TrannyTestCase):
    def __init__(self, methodName='runTest'):
        super(TrannyDBTestCase, self).__init__(methodName=methodName)
        self.init_db()

    def init_db(self, uri="sqlite://"):
        Session.remove()
        engine = create_engine(uri)
        Session.configure(bind=engine)
        Base.metadata.create_all(bind=engine)
