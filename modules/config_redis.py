import os, redis

_DEFAULT_VALUES=dict(
    last_time = '0001-01-01T00:00:00+00:00',
)

class Config(object):
    _instances = {}

    def __new__(cls, prefix, *args, **kwargs):
        if not prefix in cls._instances:
            cls._instances[prefix] = super().__new__(cls)
        return cls._instances[prefix]

    def __init__(self, prefix):
        if not self.get('_init_done', False):
            self._init_done = True
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
        if key[0] == '_': raise AttributeError()

        value = self._redis.get(self._format_key(key))
        if value is None and key in _DEFAULT_VALUES:
            value = _DEFAULT_VALUES[key]

        self._config[key] = value
        setattr(type(self), key, property(lambda self: self._getter(key), lambda self, value: self._setter(key, value)))

        return value + " - getattr"

    def _getter(self, key):
        return self._config[key]

    def _setter(self, key, value):
        self._config[key] = value

        self._redis.set(self._format_key(key), value)

        return f"{self._format_key(key)} {value} {self._redis.get(self._format_key(key))}"
