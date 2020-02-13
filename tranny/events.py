# -*- coding: utf-8 -*-

from collections import defaultdict
import logging
import time
from gevent import queue
import gevent
from tranny.exceptions import TrannyException


# Torrent events
EVENT_TORRENT_RECHECK = 'event_torrent_recheck'
EVENT_TORRENT_RECHECK_RESPONSE = 'event_torrent_recheck_response'

EVENT_TORRENT_ANNOUNCE = 'event_torrent_announce'
EVENT_TORRENT_ANNOUNCE_RESPONSE = 'event_torrent_announce_response'

EVENT_TORRENT_LIST = 'event_torrent_list'
EVENT_TORRENT_LIST_RESPONSE = 'event_torrent_list_response'

EVENT_TORRENT_STOP = 'event_torrent_stop'
EVENT_TORRENT_STOP_RESPONSE = 'event_torrent_stop_response'

EVENT_TORRENT_START = 'event_torrent_start'
EVENT_TORRENT_START_RESPONSE = 'event_torrent_start_response'

EVENT_TORRENT_PEERS = 'event_torrent_peers'
EVENT_TORRENT_PEERS_RESPONSE = 'event_torrent_peers_response'

EVENT_TORRENT_SPEED = 'event_torrent_speed'
EVENT_TORRENT_SPEED_RESPONSE = 'event_torrent_speed_response'

EVENT_TORRENT_FILES = 'event_torrent_files'
EVENT_TORRENT_FILES_RESPONSE = 'event_torrent_files_response'

EVENT_TORRENT_DETAILS = 'event_torrent_details'
EVENT_TORRENT_DETAILS_RESPONSE = 'event_torrent_details_response'

EVENT_TORRENT_REMOVE = 'event_torrent_remove'
EVENT_TORRENT_REMOVE_RESPONSE = 'event_torrent_remove_response'

EVENT_SPEED_OVERALL = 'event_speed_overall'
EVENT_SPEED_OVERALL_RESPONSE = 'event_speed_overall_response'

EVENT_UPDATE = 'event_update'
EVENT_UPDATE_RESPONSE = "event_update_response"

# To send a popup alert to the user
EVENT_ALERT = 'event_alert'

EVENT_NOTIFICATION = 'event_notification'

# Generic response
EVENT_RESPONSE = 'event_response'

EVENT_TORRENT_UPDATE = 'torrent_update'
EVENT_TORRENT_NEW = 'torrent_new'
EVENT_TORRENT_ADDED = 'torrent_added'
EVENT_TORRENT_COMPLETE = 'torrent_complete'

EVENT_TICK = 'system_tick_1'
EVENT_TICK_1 = EVENT_TICK
EVENT_TICK_5 = 'system_tick_5'
EVENT_TICK_30 = 'system_tick_30'
EVENT_TICK_60 = 'system_tick_60'


class Event(object):
    def __init__(self, event_name, payload):
        self.event_name = event_name
        self.payload = payload
        self.created_on = time.time()

    def __unicode__(self):
        return self.event_name


class EventHandler(object):
    """
    A class which will execute the event, returning the payload, modified or not
    """
    def __init__(self, event, func, priority=99):
        self.event = event
        self.func = func
        self.priority = priority

    def __call__(self, payload, *args, **kwargs):
        return self.func(payload, *args, **kwargs)

    def __unicode__(self):
        return self.func.__name__

    def __str__(self):
        return self.__unicode__().decode('latin-1')


class EventChain(object):
    """
    Process multiple events in serial. The returned payload from each event is passed to the next
    event. This way plugins can make any updated to the payload as required as it passes
    through the execution chain.
    """
    def __init__(self, events, payload):
        self.events = events
        self.payload = payload

    def __call__(self, *args, **kwargs):
        for event in self.events:
            self.payload = event(self.payload)
        return self.payload


class EventManager(object):
    """
    Handle registering and firing registered event handlers when new events are emitted
    """
    def __init__(self):
        self._event_handlers = defaultdict(list)
        self._queue = queue.PriorityQueue()
        self.log = logging.getLogger("eventmanager")

        # A group of timers to run every N seconds. This could be replaced
        # by something more intelligent pretty easily.
        self._tickers = {
            'system_tick_1': gevent.Greenlet.spawn(self.ticker, EVENT_TICK_1, 1),
            'system_tick_5': gevent.Greenlet.spawn(self.ticker, EVENT_TICK_5, 5),
            'system_tick_30': gevent.Greenlet.spawn(self.ticker, EVENT_TICK_30, 30),
            'system_tick_60': gevent.Greenlet.spawn(self.ticker, EVENT_TICK_60, 60)
        }

        # Our main event loop for executing event handlers outside of the periodic handlers
        self._event_runner = gevent.Greenlet.spawn(self.task_runner, self._queue)

    def unregister_handler(self, event_handler):
        """ Naive approach to removing handlers dynamically based on function id's


        :param event_handler: Event handler to unregister
        :type event_handler: EventHandler
        :return:
        :rtype:
        """
        for event in self.event_handlers(event_handler.event):
            if event.func is event_handler.func:
                try:
                    self._event_handlers[event_handler.event].remove(event)
                except ValueError:
                    self.log.error("Tried to remove event handler that did not exist")
                else:
                    self.log.info("Removed handler from event: {}->{}".format(event_handler.event, event))

    def register_handler(self, event_handler):
        """

        :param event_handler:
        :type event_handler: EventHandler
        :return:
        :rtype:
        """
        if event_handler.func in (f.func for f in self._event_handlers[event_handler.event]):
            self.log.warning("Tried to register event twice: {} ()".format(
                event_handler, event_handler.func))
        else:
            self._event_handlers[event_handler.event].append(event_handler)
            self._event_handlers[event_handler.event].sort(key=lambda v: v.priority)
            self.log.debug("Registered event handler [{}]: {}".format(event_handler.event, event_handler.func))

    def event_handlers(self, event):
        """

        :param event:
        :type event:
        :return:
        :rtype: []EventHandler
        """
        return self._event_handlers.get(event, [])

    def task_runner(self, q=None):
        for event in q:
            if isinstance(event, tuple):
                _, event = event
            try:
                resp = event(event)
            except TrannyException:
                self.log.exception("Uncaught internal error")
            except Exception:
                self.log.exception("Unhandled exception raised on event handler")
            else:
                return resp

    def emit(self, event, immediate=True, priority=99):
        """

        :param event:
        :type event: Event
        :param immediate:
        :type immediate:
        :param priority:
        :type priority:
        :return:
        :rtype:
        """
        if not isinstance(event, Event):
            self.log.warn("Tried to sent event with invalid type: {}".format(type(event)))
            return None
        event_handlers = self.event_handlers(event.event_name)
        if event_handlers:
            self.log.debug("Event emitted: {} [{} handlers]".format(event.event_name, len(event_handlers)))
            ec = EventChain(event_handlers, event.payload)
            if not immediate:
                self._queue.put((priority, ec))
            else:
                return self.task_runner([ec])
        else:
            self.log.debug("Event emitted: {} [0 handlers]".format(event.event_name))

    def ticker(self, event, sleep=1):
        while True:
            try:
                self.task_runner(self.event_handlers(event))
            except Exception:
                self.log.exception("Ticker unhandled exception")
            gevent.sleep(sleep)






