# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import gevent
from testcase import TrannyTestCase
from tranny import events


def e_func(payload):
    payload['a'] += 1
    return payload


def e_func_2(payload):
    payload['a'] += 2
    return payload


class EventsTest(TrannyTestCase):
    def setUp(self):
        self.event_1 = events.EventHandler(events.EVENT_TORRENT_COMPLETE, e_func, priority=1)
        self.event_2 = events.EventHandler(events.EVENT_TORRENT_COMPLETE, e_func_2, priority=1)

    def test_register_handler(self):
        em = events.EventManager()
        em.register_handler(self.event_1)
        self.assertIn(self.event_1, em.event_handlers(self.event_1.event))

    def test_event_chain(self):
        ec = events.EventChain([self.event_1, self.event_2], {'a': 1})
        payload = ec()
        self.assertEqual(payload['a'], 4)

    def test_event_emit(self):
        em = events.EventManager()
        em.register_handler(self.event_1)
        em.register_handler(self.event_2)
        resp = em.emit(self.event_1.event, {'a': 1}, immediate=True)
        self.assertEqual(resp['a'], 4)

        class A(object):
            def __init__(self, a=1):
                self.a = a

            def __call__(self, *args, **kwargs):
                self.a += 1
        incr = A()

        e = events.EventHandler('test', incr, priority=1)
        em.register_handler(e)
        em.emit('test', {'a': 1}, immediate=False)
        # wait for executor to run the task
        gevent.sleep(0.1)
        self.assertEqual(incr.a, 2)

