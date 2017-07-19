from configparser import ExtendedInterpolation
import os
from os.path import isfile, isdir, expanduser, join, dirname
import configparser

_config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
_config.read(join(dirname(__file__), 'default_config.conf'))

_HOME_FOLDER = expanduser("~")
ieml_folder = join(_HOME_FOLDER, _config.get('DEFAULT', 'iemlfolder'))
_config_file = join(ieml_folder, _config.get('DEFAULT', 'configfile'))
parser_folder = join(ieml_folder, 'parser')


if not isdir(ieml_folder):
    os.mkdir(ieml_folder)

if not isdir(parser_folder):
    os.mkdir(parser_folder)

if isfile(_config_file):
    _config.read(_config_file)


def get_configuration():
    return _config

from . import tools
from . import exceptions
from . import constants
from . import syntax
from . import dictionary
from . import usl

