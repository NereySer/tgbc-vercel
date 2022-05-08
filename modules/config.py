from .db import DbConfig

class Config(object):
    def __init__(self):
        self._db = DbConfig()

        self._config = self._db.getConfig()

        for key in self._config:
            setattr(type(self), key, property(lambda self: self._getter(key), lambda self, value: self._setter(key, value)))

    def _getter(self, name):
        return self._config[name]

    def _setter(self, key, value):
        self._config[key] = value

        self._db.setConfigValue(key, value)

