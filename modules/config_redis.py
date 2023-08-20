import os, redis

class Config(object):
    const default_values=dict(
        last_time = '0001-01-01T00:00:00+00:00',
    )

    def __init__(self, prefix):
        self._config = {}
        self._prefix = prefix

        self._redis = redis.Redis.from_url(
          os.getenv('KV_URL').replace("redis://", "rediss://"),
          charset="utf-8",
          decode_responses=True,
        )

    def _format_key(self, key):
        return f"{self._prefix}_{key}"

    def __getattr__(self, key):
        value = self._redis.get(self._format_key(key))
        if value is None and self.default_values[key] is defined:
            value = self.default_values[key]

        self._config[key] = value
        setattr(self, key, property(lambda self: self._getter(key), lambda self, value: self._setter(key, value)))

        return value

    def _getter(self, key):
        return self._config[key]

    def _setter(self, key, value):
        self._config[key] = value

        self._redis.set(self._format_key(key), value)
