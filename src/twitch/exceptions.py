class TwitchException(Exception):
    pass


class TwitchAuthException(TwitchException):
    pass


class TwitchNotProvidedError(TwitchException):
    pass
