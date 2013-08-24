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
