import logging
from configparser import ExtendedInterpolation
import os
from os.path import isfile, isdir, expanduser, join, dirname
import configparser
import sys

from appdirs import user_cache_dir, user_data_dir

from ieml.constants import LIBRARY_VERSION

_config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
_config.read(join(dirname(__file__), 'default_config.conf'))

VERSIONS_FOLDER = os.path.join(user_data_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION), 'dictionary_versions')

CACHE_VERSIONS_FOLDER = os.path.join(user_cache_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION), 'cached_dictionary_versions')
PARSER_FOLDER = os.path.join(user_cache_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION), 'parsers')


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


if not isdir(VERSIONS_FOLDER):
    os.makedirs(VERSIONS_FOLDER)

if not isdir(PARSER_FOLDER):
    os.makedirs(PARSER_FOLDER)

if not isdir(CACHE_VERSIONS_FOLDER):
    os.makedirs(CACHE_VERSIONS_FOLDER)

# if isfile(_config_file):
#     _config.read(_config_file)

init_logging(_config)

def get_configuration():
    return _config
