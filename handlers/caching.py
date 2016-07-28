import functools
from os import makedirs
from os.path import dirname, join, isdir

from werkzeug.contrib.cache import FileSystemCache
import logging

CACHE_TIMEOUT = 300
CACHE_DIRNAME = join(dirname(__file__), "cache")

if not isdir(CACHE_DIRNAME):
    try:
        makedirs(CACHE_DIRNAME)
    except OSError:
        pass

cache = FileSystemCache(CACHE_DIRNAME)


def flush_cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cache.delete("all_ieml")
        logging.debug("Cache cleared")
        return func(*args, **kwargs)
    return wrapper


class cached(object):

    def __init__(self, cache_key, timeout=None):
        self.timeout = timeout or CACHE_TIMEOUT
        self.cache_key = cache_key

    def __call__(self, f):
        def decorator(*args, **kwargs):
            cached_value = cache.get(self.cache_key)
            if cached_value is None:
                cached_value = f(*args, **kwargs)
                cache.set(self.cache_key, cached_value, self.timeout)
            return cached_value

        return decorator

kwd_mark = object


# Might be used for something else, this cache uses arguments as a key.
class memoized(object):

    def __init__(self, cache_key, timeout=None):
        self.timeout = timeout or CACHE_TIMEOUT
        self.cache_key = cache_key

    def __call__(self, f):
        def decorator(*args, **kwargs):
            key = args + (kwd_mark, self.cache_key) + tuple(sorted(kwargs.items().__hash__()))
            cached_value = cache.get(key)
            if cached_value is None:
                cached_value = f(*args, **kwargs)
                cache.set(key, cached_value, self.timeout)
            return cached_value

        return decorator