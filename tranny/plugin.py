# -*- coding: utf-8 -*-

import logging
from abc import ABCMeta, abstractmethod
from tranny import events


class BasePlugin(object, metaclass=ABCMeta):
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
    """
    Very trivial example plugin that prints out "Plugin tick!" every second
    using the 1 second event ticker
    """
    def __init__(self):
        super(ExamplePlugin, self).__init__('example')
        self.event_handlers = [
            events.EventHandler(events.EVENT_TICK_1, lambda v: self.log.info("Plugin tick!"))
        ]

    def get_handlers(self):
        """

        :return:
        :rtype: []EventHandler
        """
        return self.event_handlers


class PluginManager(object):
    """ Handle registering and tracking plugins for the event manager. You can think of this as
    a public facing version of the event_manager that 3rd party users would interact with. Where as
    the EventManager instance is used for internal event handlers mostly and is not meant to support
    additions from 3rd parties.
    """
    def __init__(self, event_manager):
        """ Takes the event manager as a dependency

        :param event_manager:
        :type event_manager: tranny.events.EventManager
        """
        self.event_manager = event_manager
        self.loaded_plugins = {}
        self.log = logging.getLogger("PluginManager")

    def register(self, plugin):
        """ Register a plugin and bind its handler functions to the events

        .. note:: Not sure of the best way to handle this. Use weak ref's and del the parent instance to clear
         all children maybe?

        :param plugin:
        :type plugin: BasePlugin
        :return: True on success
        :rtype: bool
        """
        if not isinstance(plugin, BasePlugin):
            raise TypeError("Cannot register plugin that does not subclass plugin.BasePlugin")
        if self.is_loaded(plugin):
            raise ValueError("Plugin already registered: {}".format(plugin.name))
        self.loaded_plugins[plugin.name] = plugin
        for handler in plugin.get_handlers():
            self.event_manager.register_handler(handler)
        self.log.info("Registered plugin: {}".format(plugin.name))
        return True

    def unregister(self, plugin):
        """ Unregister all of the handlers associated with the plugin provided

        :param plugin: Plugin instance, or plugin name
        :type plugin: BasePlugin
        :return: Remove status
        :rtype: bool
        """
        try:
            handlers = self.loaded_plugins[self._get_name(plugin)].get_handlers()
        except KeyError:
            self.log.warning("Tried to unregister a non-registered plugin: {}".format(plugin))
            return False
        else:
            removed = 0
            for handler in handlers:
                self.event_manager.unregister_handler(handler)
                removed += 1
            remove_ok = len(handlers) == removed
            if remove_ok:
                try:
                    del self.loaded_plugins[self._get_name(plugin)]
                except KeyError:
                    self.log.warning("Failed to remove plugin completely")
            return remove_ok

    def _get_name(self, plugin):
        """ Simple function to allow a plugin string name or an plugin instance to be used
        as an identifier for the plugin registration

        :param plugin: Plugin instance or plugin string name to use
        :type plugin: BasePlugin
        :return: Plugin string name
        :rtype: unicode
        """
        return plugin.name if isinstance(plugin, BasePlugin) else plugin

    def is_loaded(self, plugin):
        """ Test if the plugin is already known in the system

        :param plugin: Plugin or name to check
        :type plugin: BasePlugin
        :return: Plugin is loaded status
        :rtype: bool
        """
        return self._get_name(plugin) in self.loaded_plugins
