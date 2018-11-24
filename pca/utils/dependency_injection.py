from enum import Enum
from functools import partial
from typing import (
    Any,
    Callable,
    Union,
)

NameOrInterface = Union[type, str]


class Container:
    def __init__(self, default_scope: 'Scopes'=None):
        self._registry = {}
        self._default_scope_function = default_scope

    @staticmethod
    def _get_registry_key(identifier: NameOrInterface, qualifier: Any=None) -> tuple:
        return identifier, qualifier,

    def register_by_name(self, name: str, constructor: Callable):
        key = Container._get_registry_key(name)  # TODO: qualifier
        if key in self._registry:
            raise ValueError(f'Ambiguous name: {name}.')
        self._registry[key] = constructor

    def find_by_name(self, name: str) -> Any:
        key = Container._get_registry_key(name)  # TODO: qualifier
        return self.get_object(self._registry.get(key))

    def get_object(self, constructor: Callable) -> Any:
        call = getattr(constructor, '__scope_function', self._default_scope_function)
        return call(self, constructor)

    def find_by_interface(self, interface):
        raise NotImplementedError

    def register_by_interface(self, interface):
        raise NotImplementedError

    def instance_scope(self, constructor: Callable) -> Any:
        return constructor()


class Scopes(Enum):
    INSTANCE = partial(Container.instance_scope)

    def __call__(self, container: Container, constructor: Callable):
        return self.value(container, constructor)

    def __repr__(self):
        return f"<Scopes.{self.name}>"


def scope(scope_type: Scopes) -> Callable:
    def decorator(obj: Callable) -> Callable:
        obj.__scope_function = scope_type
        return obj
    return decorator
