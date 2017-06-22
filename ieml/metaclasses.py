import logging


class LoggedInstantiator(type):
    def __call__(cls, *args, **kwargs):
        logging.debug("Created a %s instance" % cls.__name__)
        # we need to call type.__new__ to complete the initialization
        return super(LoggedInstantiator, cls).__call__(*args, **kwargs)


def fullname(cls):
    return cls.__module__ + '.' + cls.__qualname__


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # this code is to clean up duplicate class if we reload modules
            to_remove = [i for i in cls._instances if fullname(i) == fullname(cls)]
            for i in to_remove:
                del cls._instances[i]

            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]