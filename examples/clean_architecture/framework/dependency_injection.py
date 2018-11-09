# -*- coding: utf-8 -*-
import typing as t


class AbstractContainer:
    """
    Abstract class of the DI container. Subclasses should know how to
    construct all the dependencies, ie:
        * config,
        * settings,
        * local store based on session,
        * connectors aka database table objects
        * etc
    """

    def find(self, interface):
        """Find the dependency described with the given interface."""
        raise NotImplementedError


class Inject:
    """
    A descriptor for injecting dependencies as properties

    .. code-block:: python

        class SomeClass:
            my_dep: DepType = Inject()

    .. important::

        Dependency is injected (created/fetched) at the moment of attribute
        access, not instance of `SomeClass` creation. So, even if you create
        an instance of `SomeClass`, the instance of `DepType` may never be
        created.
    """

    def __init__(self, qualifier: str = None):
        self._qualifier = qualifier
        self._type: t.Type = None
        self.__owner: t.Any = None
        self.__prop_name: str = None

    def __get__(self, instance: t.Any, owner: t.Type) -> t.Any:
        if instance is None:
            return self
        else:
            obj = getattr(instance, self.__prop_name, None)
            if obj is None:
                obj = Container().get_object(self.type_, self._qualifier)
                setattr(instance, self.__prop_name, obj)
            return obj

    def __set_name__(self, owner: t.Type, name: str) -> None:
        self.__owner = owner
        self.__prop_name = name
        type_: t.Type = owner.__annotations__.get(name)
        if type_ is not None:
            self.type_ = type_
        else:
            raise TypeError('No annotation for Inject')
