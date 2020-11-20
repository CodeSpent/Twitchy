from datetime import datetime


def convert_to_twitch_object(name, data):
    types = {"user": User}

    special_types = {
        "created_at": _DateTime,
        "updated_at": _DateTime,
        "started_at": _DateTime,
        "followed_at": _DateTime,
    }

    if isinstance(data, list):
        return [convert_to_twitch_object(name, x) for x in data]

    if isinstance(data, dict) and name in types:
        obj = types.get(name)
        return obj.construct(data)

    if name in special_types:
        obj = special_types.get(name)
        return obj.construct(data)

    return data


class TwitchObject(dict):
    def __setattr__(self, name, value):
        if name[0] == "_" or name in self.__dict__:
            return super(TwitchObject, self).__setattr__(name, value)

    def __getattr__(self, name):
        return self[name]

    def __delattr__(self, name):
        if name[0] == "_":
            return super(TwitchObject, self).__delattr__(name)

        del self[name]

    def __setitem__(self, key, value):
        key = key.lstrip("_")
        super(TwitchObject, self).__setitem__(key, value)

    @classmethod
    def construct(cls, values):
        instance = cls()
        instance.refresh(values)
        return instance

    def refresh(self, values):
        for key, value in values.copy().items():
            self.__setitem__(key, convert_to_twitch_object(key, value))


class _DateTime(object):
    @classmethod
    def construct(cls, value):
        if value is None:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")


class User(TwitchObject):
    pass


class Cheermote(TwitchObject):
    pass


class Clip(TwitchObject):
    pass


class Game(TwitchObject):
    pass


class HypeTrainEvent(TwitchObject):
    pass


class BannedUser(TwitchObject):
    pass


class BanEvent(TwitchObject):
    pass


class ModeratorEvent(TwitchObject):
    pass


class StreamKey(TwitchObject):
    pass


class Stream(TwitchObject):
    pass


class StreamMarker(TwitchObject):
    pass


class Channel(TwitchObject):
    pass


class Subscription(TwitchObject):
    pass


class StreamTag(TwitchObject):
    pass


class Follow(TwitchObject):
    pass


class Extension(TwitchObject):
    pass


class Video(TwitchObject):
    pass


class WebhookSubscription(TwitchObject):
    pass


class Commercial(TwitchObject):
    pass
