import os, redis

_DEFAULT_VALUES=dict(
    last_time = '0001-01-01T00:00:00+00:00',
)

class Config(object):
    _instances = {}

    def __new__(cls, prefix, *args, **kwargs):
        if not prefix in cls._instances:
            self = super().__new__(cls)

            self._prefix = prefix
            self._redis = redis.Redis.from_url(
              os.getenv('KV_URL').replace("redis://", "rediss://"),
              charset="utf-8",
              decode_responses=True,
            )

            cls._instances[prefix] = self

        return cls._instances[prefix]

    def _format_key(self, key):
        return f"{self._prefix}_{key}"

    def __getattr__(self, key):
        if key[0] == '_': raise AttributeError()

        value = self._redis.get(self._format_key(key))
        if value is None and key in _DEFAULT_VALUES:
            value = _DEFAULT_VALUES[key]

        return value

    def __setattr__(self, key, value):
        if key[0] == '_':
            self.__dict__[key] = value
        else:
            self._redis.set(self._format_key(key), value)
