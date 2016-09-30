# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json

try:
    import yaml
except ImportError:
    yaml = None

# noinspection PyUnresolvedReferences
from six.moves import configparser as _configparser


def configparser(filenames):
    config = _configparser.ConfigParser()
    return config.read(filenames)


DESERIALIZERS = {
    'json': json,
    'yaml': yaml,
    'configparser': configparser,
}
