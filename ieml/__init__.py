from configparser import ExtendedInterpolation
import os
from os.path import isfile, isdir, expanduser, join, dirname
import configparser

_config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
_config.read(join(dirname(__file__), 'default_config.conf'))

_HOME_FOLDER = expanduser("~")
ieml_folder = join(_HOME_FOLDER, _config.get('DEFAULT', 'iemlfolder'))
_config_file = join(ieml_folder, _config.get('DEFAULT', 'configfile'))

if not isdir(ieml_folder):
    os.mkdir(ieml_folder)

if isfile(_config_file):
    _config.read(_config_file)


def get_configuration():
    return _config



