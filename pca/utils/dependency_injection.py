from enum import Enum
from typing import (
    Any,
    Callable,
    Union,
)

NameOrInterface = Union[type, str]


class Container:
    def __init__(self):
        self._registry = {}
        self.default_scope = Scopes.INSTANCE

    def register_by_name(self, name: str, constructor: Callable):
        key = Container._get_registry_key(name)  # TODO: qualifier
        if key in self._registry:
            raise ValueError(f'Ambiguous name: {name}.')
        self._registry[key] = constructor

    @staticmethod
    def _get_registry_key(identifier: NameOrInterface, qualifier: Any=None) -> tuple:
        return identifier, qualifier,

    def find_by_name(self, name: str) -> Any:
        key = Container._get_registry_key(name)  # TODO: qualifier
        return self.get_object(self._registry.get(key))

    def get_object(self, constructor: Callable) -> Any:
        call = getattr(constructor, '__scope_type', self.default_scope)
        return call(self, constructor)

    def find_by_interface(self, interface):
        raise NotImplementedError

    def register_by_interface(self, interface):
        raise NotImplementedError

    def instance_scope(self, constructor: Callable) -> Any:
        return constructor()


class Scopes(Enum):
    INSTANCE = Container.instance_scope


def scope(scope_type: Callable) -> Callable:
    def decorator(obj: Callable) -> Callable:
        obj.__scope_type = scope_type
        return obj
    return decorator
