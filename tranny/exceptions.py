# -*- coding: utf-8 -*-
from __future__ import unicode_literals


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
    def __init__(self, error):
        self.message = error['message']
        self.err_code = error['code']


class AuthenticationError(ApiError):
    pass


class ClientNotAvailable(InvalidResponse):
    pass
