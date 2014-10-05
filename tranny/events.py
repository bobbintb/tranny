# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from collections import defaultdict
import logging
from gevent import queue
import gevent
from tranny.exceptions import TrannyException


EVENT_TORRENT_COMPLETE = 'torrent_complete'
EVENT_TICK = 'system_tick_1'
EVENT_TICK_1 = EVENT_TICK
EVENT_TICK_5 = 'system_tick_5'
EVENT_TICK_30 = 'system_tick_30'
EVENT_TICK_60 = 'system_tick_60'


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


class EventChain(object):
    def __init__(self, events, payload):
        self.events = events
        self.payload = payload

    def __call__(self, *args, **kwargs):
        for event in self.events:
            self.payload = event(self.payload)
        return self.payload


class EventManager(object):

    def __init__(self):
        self._event_handlers = defaultdict(list)
        self._queue = queue.PriorityQueue()
        self.log = logging.getLogger("eventmanager")

        self._tickers = {
            1: gevent.Greenlet.spawn(self.ticker, EVENT_TICK_1, 1),
            5: gevent.Greenlet.spawn(self.ticker, EVENT_TICK_5, 5),
            30: gevent.Greenlet.spawn(self.ticker, EVENT_TICK_30, 30),
            60: gevent.Greenlet.spawn(self.ticker, EVENT_TICK_60, 60)
        }
        self._event_runner = gevent.Greenlet.spawn(self.executor)

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

    def executor(self, q=None):
        if q is None:
            q = self._queue
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

    def emit(self, event, payload, immediate=True, priority=99):
        if not event:
            return None
        events = self.event_handlers(event)
        if events:
            ec = EventChain(events, payload)
            if not immediate:
                self._queue.put((priority, ec))
            else:
                return self.executor([ec])

    def ticker(self, event, sleep=1):
        while True:
            try:
                self.executor(self.event_handlers(event))
            except Exception:
                self.log.exception("Ticker unhandled exception")
            gevent.sleep(sleep)






