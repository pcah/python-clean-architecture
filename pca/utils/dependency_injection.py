from enum import Enum
from typing import Union, Any, Callable

NameOrInterface = Union[type, str]


def instance_scope(container: 'Container', constructor: Callable) -> Any:
    return constructor()


class Scopes(Enum):
    INSTANCE = instance_scope


class Container:
    def __init__(self):
        self._registry = {}

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

    def get_object(self, constructor: type) -> Any:
        call = getattr(constructor, '__scope_type', Scopes.INSTANCE)
        return call(self, constructor)

    def find_by_interface(self, interface):
        raise NotImplementedError

    def register_by_interface(self, interface):
        raise NotImplementedError


def scope(scope_type: str) -> Callable:
    def decorator(class_: type) -> type:
        class_.__scope_type = scope_type
        return class_
    return decorator
