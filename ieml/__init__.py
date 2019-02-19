import logging
from configparser import ExtendedInterpolation
from os.path import join, dirname
import configparser
import sys
from .ieml_database import IEMLDatabase


from ieml.constants import LIBRARY_VERSION

_config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
_config.read(join(dirname(__file__), 'default_config.conf'))

def init_logging(config):
    level = getattr(logging, config.get('DEFAULT', 'loglevel').upper())
    if not isinstance(level, int):
        raise ValueError('Invalid log level: %s' % level)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    try:
        file = config.get('DEFAULT', 'logfile')
    except configparser.NoOptionError:
        pass
    else:
        fh = logging.FileHandler(file)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        root.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    root.addHandler(ch)



# if isfile(_config_file):
#     _config.read(_config_file)

init_logging(_config)

def get_configuration():
    return _config
