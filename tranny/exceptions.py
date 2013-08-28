# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class TrannyException(Exception):
    pass


class BotchedTranny(TrannyException):
    """ General application error """
    pass


class ConfigError(BotchedTranny):
    """ Application configuration error """
    pass


class InvalidResponse(BotchedTranny):
    pass
