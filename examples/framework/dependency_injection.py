# -*- coding: utf-8 -*-
from enum import Enum
from functools import partial
import typing as t


class Container:
    """
    Class of the DI container. Subclasses should know how to
    construct all the dependencies, ie:
        * config,
        * settings,
        * local store based on session,
        * connectors aka database table objects
        * etc
    """
    def __init__(self, default_scope: 'Scopes',
                 request_strategy: t.Callable = None,
                 session_strategy: t.Callable = None):
        self.default_scope = default_scope
        self.request_strategy = request_strategy
        self.session_strategy = session_strategy

    def load_from_file(self, filepath):
        """Loads container sets from content of a file"""

    def register_interface(self, interface: t.Type, constructor: t.Callable,
                           qualifier: t.Any=None, kwargs: t.Mapping=None):
        """Find the dependency described with the given interface."""
        raise NotImplementedError

    def find_by_interface(self, interface: t.Type, qualifier: t.Any=None,
                          kwargs: t.Mapping = None):
        """Find the dependency described with the given interface."""
        raise NotImplementedError

    def instance_scope(self, constructor: t.Callable):
        raise NotImplementedError

    def request_scope(self, constructor: t.Callable):
        raise NotImplementedError

    def session_scope(self, constructor: t.Callable):
        raise NotImplementedError

    def thread_scope(self, constructor: t.Callable):
        raise NotImplementedError

    def singleton_scope(self, constructor: t.Callable):
        raise NotImplementedError


class Scopes(Enum):
    INSTANCE = partial(Container.instance_scope)  # every injection makes a new instance
    REQUEST = partial(Container.request_scope)  # per a "request" (whatever a request is in your application)
    SESSION = partial(Container.session_scope)  # per session (whatever is a user session in your application)
    THREAD = partial(Container.thread_scope)  # per thread (via `threading.local`)
    SINGLETON = partial(Container.singleton_scope)  # always the same instance in this container

    def __call__(self, container: Container, constructor: t.Callable):
        return self.value(container, constructor)

    def __repr__(self):
        return f"<Scopes.{self.name}>"


class Inject:
    """
    A descriptor for injecting dependencies as properties

    .. important::

        Dependency is injected (created/fetched) at the moment of attribute
        access, not instance of `SomeClass` creation. So, even if you create
        an instance of `SomeClass`, the instance of `DepType` may never be
        created.
    """

    def __init__(self, qualifier: t.Any = None):
        self._qualifier = qualifier
        self._interface: t.Type = None
        self.__owner: t.Any = None
        self.__field_name: str = None

    def __set_name__(self, owner: t.Type, name: str) -> None:
        assert getattr(owner, 'container', None), \
            f"No container on this traits owner class ({owner.__qualname__})"
        # noinspection PyUnresolvedReferences
        self._container = owner.container
        self.__owner = owner
        self.__field_name = name
        _interface: t.Type = owner.__annotations__.get(name)
        if _interface is not None:
            self._interface = _interface
        else:
            # TODO resolution by name, then raise ConfigurationError
            raise ConfigurationError('No annotation for Inject')

    def __get__(self, instance: t.Any, owner: t.Type) -> t.Any:
        if instance is None:
            return self
        obj = getattr(instance, self.__field_name, None)
        if obj is None:
            obj = self._container.find_by_interface(self._interface, self._qualifier)
            setattr(instance, self.__field_name, obj)
        return obj
