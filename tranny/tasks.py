# -*- coding: utf-8 -*-

import gevent
from gevent import queue


class Task(object):
    def __init__(self, func, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.func = func

    def __call__(self):
        self.func(*self.args, **self.kwargs)


def consumer():
    while True:
        try:
            task = _task_queue.get()
        except queue.Empty:
            pass
        else:
            try:
                task()
            finally:
                _task_queue.task_done()


def add_task(task):
    _task_queue.put_nowait(task)


_running_tasks = {}
_task_queue = queue.JoinableQueue()
_consumer = gevent.spawn(consumer)
