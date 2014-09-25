# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import


class TrannyException(Exception):
    """ Base exception used for application generated exceptions """
    pass


class BotchedTranny(TrannyException):
    """ General application error """
    pass


class ConfigError(BotchedTranny):
    """ Application configuration error """
    pass


class InvalidResponse(BotchedTranny):
    pass


class ClientError(TrannyException):
    pass


class ApiError(BotchedTranny):
    pass


class AuthenticationError(ApiError):
    pass


class ClientNotAvailable(InvalidResponse):
    pass

class ParseError(BotchedTranny):
    pass
