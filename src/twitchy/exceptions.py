class TwitchException(Exception):
    pass


class TwitchAuthException(TwitchException):
    pass


class TwitchNotProvidedError(TwitchException):
    pass


class TwitchValueError(ValueError):
    pass


class TwitchAttributeError(AttributeError):
    pass
