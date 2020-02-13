# -*- coding: utf-8 -*-



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


class EventHandlerError(TrannyException):
    pass


class EventChainStop(EventHandlerError):
    """ Raised to stop an event chain in progress """
    pass


class EventChainContinue(EventHandlerError):
    pass
