#!/usr/bin/env python
from logging import  basicConfig
from tranny import config, Tranny

log_level = config.getint('log', 'level')
basicConfig(level=log_level)
tr = Tranny()
tr.init()
tr.run_forever()
