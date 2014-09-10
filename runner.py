# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals, absolute_import
import gevent
from tranny import manager

app = manager.ServiceManager()
app.start()

while True:
    gevent.sleep(1)
