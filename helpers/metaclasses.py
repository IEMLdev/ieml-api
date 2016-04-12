import logging

class LoggedInstantiator(type):
    def __call__(cls, *args, **kwargs):
        logging.debug("Created a %s instance" % cls.__name__)
        # we need to call type.__new__ to complete the initialization
        return super(LoggedInstantiator, cls).__call__(*args, **kwargs)


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]