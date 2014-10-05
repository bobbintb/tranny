# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
from abc import ABCMeta, abstractmethod
from tranny import events


class BasePlugin(object):
    __metaclass__ = ABCMeta

    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger('plugin.{}'.format(name))

    @abstractmethod
    def get_handlers(self):
        """

        :return:
        :rtype: []EventHandler
        """
        return []


class ExamplePlugin(BasePlugin):

    def __init__(self):
        super(ExamplePlugin, self).__init__('example')
        self.event_handlers = [
            events.EventHandler(events.EVENT_TICK, lambda v: self.log.info("Plugin tick!"))
        ]

    def get_handlers(self):
        """

        :return:
        :rtype: []EventHandler
        """
        return self.event_handlers


class PluginManager(object):
    def __init__(self, event_manager):
        """

        :param event_manager:
        :type event_manager: EventManager
        :return:
        :rtype:
        """
        self.event_manager = event_manager
        self.loaded_plugins = {}

    def register(self, plugin):
        """

        :param plugin:
        :type plugin: BasePlugin
        :return:
        :rtype:
        """
        if not isinstance(plugin, BasePlugin):
            raise TypeError("Cannot register plugin that does not subclass plugin.BasePlugin")
        if plugin.name in self.loaded_plugins:
            raise ValueError("Plugin already registered: {}".format(plugin.name))
        self.loaded_plugins[plugin.name] = plugin
        map(self.event_manager.register_handler, plugin.get_handlers())

    def unregister(self, plugin):
        pass

