# -*- coding: utf-8 -*-
"""

"""

from .testcase import TrannyTestCase
from tranny import events
from tranny import plugin


class TestPlugin(plugin.BasePlugin):

    def __init__(self):
        super(TestPlugin, self).__init__('test')
        self.event_handlers = [
            events.EventHandler(events.EVENT_TICK, lambda v: self.log.info("Plugin tick!"))
        ]

    def get_handlers(self):
        """

        :return:
        :rtype: []EventHandler
        """
        return self.event_handlers


class PluginTest(TrannyTestCase):

    def setUp(self):
        self.em = events.EventManager()
        self.pm = plugin.PluginManager(self.em)
        self.plugin = TestPlugin()

    def test_register_plugin(self):
        self.assertTrue(self.pm.register(self.plugin))
        self.assertIn(self.plugin.name, self.pm.loaded_plugins)
        self.assertTrue(self.pm.is_loaded(self.plugin))
        self.assertTrue(self.pm.is_loaded(self.plugin.name))

    def test_unregister_plugin(self):
        self.assertTrue(self.pm.register(self.plugin))
        self.assertIn(self.plugin.name, self.pm.loaded_plugins)
        self.assertTrue(self.pm.is_loaded(self.plugin))
        self.pm.unregister(self.plugin)
        self.assertNotIn(self.plugin.name, self.pm.loaded_plugins)
