# -*- coding: utf-8 -*-
import errno
import os
import six

from dharma.compat.serializers import configparser, json, yaml
from dharma.exceptions import DharmaConfigError
from .imports import import_dotted_path


class Config(dict):
    """
    Works exactly like a dict but provides ways to fill it from files
    or special dictionaries.  There are two common patterns to populate the
    config.

    Either you can fill the config from a config file::

        Config.from_pyfile('your_config.json')

    Or alternatively you can define the configuration options in the
    module that calls :meth:`from_object` or provide an import path to
    a module that should be loaded.  It is also possible to tell it to
    use the same module and with that provide the configuration values
    just before the call::

        DEBUG = True
        SECRET_KEY = 'development key'
        config.from_object(__name__)

    In both cases (loading from any Python file or loading from modules),
    only uppercase keys are added to the config.  This makes it possible to use
    lowercase values in the config file for temporary values that are not added
    to the config or to define the config keys in the same file that implements
    the application.

    Probably the most interesting way to load configurations is from an
    environment variable pointing to a file::

        config.from_envvar('YOURAPPLICATION_SETTINGS')

    Taken from Flask, v. 0.11.1
    """

    @classmethod
    def from_mapping(cls, mapping, silent=False):
        # type: (Mapping, bool) -> Config
        """
        Creates the config from a Mapping (dict or similar) ignoring private
        items keys. A key is private iff function 'is_key_private' says so.
        """
        return Config(
            (key, value) for key, value in six.iteritems(mapping)
            if not is_key_private(key)
        )

    def update_with_mapping(self, mapping, silent=False):
        # type: (Mapping, bool) -> None
        """
        Updates the config from a Mapping (dict or similar) ignoring private
        items keys. A key is private iff function 'is_key_private' says so.
        """
        # nnoinspection PyTypeChecker
        self.update(
            (key, value) for key, value in six.iteritems(mapping)
            if not is_key_private(key)
        )

    @classmethod
    def from_object(cls, obj, silent=False):
        # type: (Any, bool) -> Config
        """Updates the values from the given object.  An object can be of one
        of the following two types:

        -   a string: in this case the object with that name will be imported
        -   an actual object reference: that object is used directly

        Objects are usually either modules or classes. :meth:`from_object`
        loads only the uppercase attributes of the module/class. A ``dict``
        object will not work with :meth:`from_object` because the keys of a
        ``dict`` are not attributes of the ``dict`` class.

        Example of module-based configuration::

            app.config.from_object('yourapplication.default_config')
            from yourapplication import default_config
            app.config.from_object(default_config)

        You should not use this function to load the actual configuration but
        rather configuration defaults.  The actual config should be loaded
        with :meth:`from_pyfile` and ideally from a location not within the
        package because the package might be installed system wide.

        :param obj: an import name or object
        """
        return Config(
            (key, getattr(obj, key)) for key in dir(obj)
            if not is_key_private(str(key))
        )

    @classmethod
    def from_dotted_path(cls, path, silent=False):
        # type: (str, bool) -> Config
        try:
            obj = import_dotted_path(path)
        except ImportError:
            if silent:
                return Config()
            six.reraise()
        else:
            return cls.from_object(obj, silent)

    @classmethod
    def from_file(cls, path, deserializer=None, silent=False):
        # type: (str, Callable[[str], Mapping], bool) -> Config
        """
        Creates a Config from a file using a deserializer (JSON).
        If deserializer hasn't been given, it tries to guess the deserializer
        based on file extension in the path.

        :param path: the path to the config file.  This can either be an
            absolute filename or a filename relative to the root path.
        :param deserializer: a function which takes content of the file and
            return a mapping (ie. dict) with the content of the Config.
            It might be a ie. json.loads or yaml.load.
        :param silent: set to `True` if you want silent failure for missing
            files.
        """
        path = get_filepath(path)
        deserializer = deserializer or guess_deserializer(path)
        if not deserializer:
            if silent:
                return Config()
            raise DharmaConfigError("Deserializer hasn't been specified and it")

        try:
            obj = load_from_file(path, deserializer)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return Config()
            raise DharmaConfigError(
                "Unable to load configuration file (%s)" % e.strerror
            )
        else:
            return cls.from_mapping(obj)

    @classmethod
    def from_envvar(self, variable_name, deserializer=None, silent=False):
        # type: (str, Callable[[str], Mapping], bool) -> Config
        """
        Loads a configuration from an environment variable pointing to
        a configuration file.  This is basically just a shortcut with nicer
        error messages for this line of code::

            app.config.from_pyfile(os.environ['YOURAPPLICATION_SETTINGS'])

        :param variable_name: name of the environment variable
        :param deserializer: a function which takes content of the file and
            return a mapping (ie. dict) with the content of the Config.
            It might be a ie. json.loads or yaml.load.
        :param silent: set to `True` if you want silent failure for missing
            files and/or .
        """
        path = os.environ.get(variable_name)
        if not path:
            if silent:
                return Config()
            raise DharmaConfigError(
                "The environment variable %r is not set and as such "
                "configuration could not be loaded.  Set this variable and "
                "make it point to a configuration file" % variable_name
            )
        return self.from_file(path, deserializer=deserializer, silent=silent)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))


def is_key_private(key):
    # type: (str) -> bool
    """
    Predicate defining iff key is 'private' and shouldn't be put into the config.
    """
    return hasattr(key, 'startswith') and key.startswith('_')


def get_filepath(path):
    # type: (str) -> str
    """
    Returns a filepath to a config file, based on filepath given.

    Basicly, this is identity function. Monkeypatch it if you have troubles
    with relative path to config's directory or want to shorten the paths.
    """
    return path


def load_from_file(path, deserializer):
    # type: (str, Callable[[str], Mapping], bool) -> Any
    """
    Returns object build with a deserializer based on a content of a file,
    specified by a given path.

    Raises:
        * IOError - if file can't be read
        * deserializer-specific error
    """
    with open(path) as file:
        obj = deserializer(file.read())
    return obj


def guess_deserializer(filepath):
    # type: (str) -> Callable[[str], Mapping]
    """
    Tries to guess deserializer function basing on the filepath.
    :param filepath:
    """
    if any(filepath.endswith(ext) for ext in ('yaml', 'yml')):
        return yaml.load
    if any(filepath.endswith(ext) for ext in ('cfg', 'config')):
        return configparser
    return json.loads


def register_yaml_constructor():
    """
    Allows YAML constructor create sub-Config instances based on string
    treated as a filepath to a config file.
    """
    def config_constructor(loader, node):
        filepath = loader.construct_scalar(node)
        return Config.from_file(filepath)

    yaml.add_constructor(u'!Config', config_constructor)


if yaml:
    register_yaml_constructor()
