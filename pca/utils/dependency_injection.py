import inspect
from enum import Enum
from functools import partial, wraps
import typing as t

from pca.exceptions import DependencyNotFoundError


NameOrInterface = t.Union[type, str]
Constructor = t.Union[t.Type, t.Callable]
Kwargs = t.Dict[str, t.Any]  # keyword-arguments of a Constructor
ScopeFunction = t.Callable[[Constructor, Kwargs], t.Any]

_SCOPE_TYPE_REF = '__scope_type'


class Container:
    """
    Dependency Injection container. It's passed as an argument of every dependency
    injection aware constructor.
    """

    def __init__(self, default_scope: 'Scopes' = None):
        self._constructor_registry = {}
        self._singleton_registry = {}
        self._default_scope = default_scope

    @staticmethod
    def _get_registry_key(identifier: NameOrInterface, qualifier: t.Any = None) -> tuple:
        return identifier, qualifier,

    def register_by_name(
            self,
            name: str,
            constructor: Constructor,
            qualifier: t.Any = None,
            kwargs: Kwargs = None,
            scope: 'Scopes' = None,
    ):
        """
        Registering constructors by name and (optional) qualifier.

        :param name: name as the identifier of the constructor registration
        :param constructor: a type or a callable that can construct an instance of the dependency.
            Expected signature: (Container, **kwargs) -> dependency_instance
        :param qualifier: (optional) arbitrary object to narrow the context of identifying
            the constructor. The typical use case is a situation when multiple constructors are
            registered for the same interface, but for different target components.
        :param kwargs: (optional) keyword arguments of the constructor
        :param scope: (optional) scope of the registration. If provided, it defines when
            the constructor is called to provide a new instance of the dependency. It overrides
            scope declared with a `scope` decorator on the constructor, if any, and the default
            scope of the container.
        """
        self._register(
            identifier=name, constructor=constructor, qualifier=qualifier,
            kwargs=kwargs, scope=scope
        )

    def register_by_interface(
            self,
            interface: type,
            constructor: Constructor,
            qualifier: t.Any = None,
            kwargs: Kwargs = None,
            scope: 'Scopes' = None,
    ):
        """
        Registering constructors by interface and (optional) qualifier.

        :param interface: a type that defines API of the injected dependency.
        :param constructor: a type or a callable that can construct an instance of the dependency.
            Expected signature: (Container, **kwargs) -> dependency_instance
        :param qualifier: (optional) arbitrary object to narrow the context of identifying
            the constructor. The typical use case is a situation when multiple constructors are
            registered for the same interface, but for different target components.
        :param kwargs: (optional) keyword arguments of the constructor
        :param scope: (optional) scope of the registration. If provided, it defines when
            the constructor is called to provide a new instance of the dependency. It overrides
            scope declared with a `scope` decorator on the constructor, if any, and the default
            scope of the container.

        """
        # TODO Refs #20: should I register superclasses of the interface as well?
        self._register(
            identifier=interface, constructor=constructor, qualifier=qualifier,
            kwargs=kwargs, scope=scope
        )

    def _register(
        self,
        identifier: NameOrInterface,
        constructor: Constructor,
        qualifier: t.Any = None,
        kwargs: Kwargs = None,
        scope: 'Scopes' = None,
    ):
        """Technical detail of registering a constructor"""
        key = Container._get_registry_key(identifier, qualifier)
        if key in self._constructor_registry:
            raise ValueError(f'Ambiguous identifier: {identifier}.')
        self._constructor_registry[key] = (constructor, kwargs)
        if scope is not None:
            setattr(constructor, _SCOPE_TYPE_REF, scope)

    def find_by_name(self, name: str, qualifier: t.Any = None) -> t.Any:
        """Finding registered constructor by name."""
        return self._find(identifier=name, qualifier=qualifier)

    def find_by_interface(self, interface: type, qualifier: t.Any = None) -> t.Any:
        """Finding registered constructor by interface."""
        # TODO Refs #20: should I look for the subclasses of the interface as well?
        return self._find(identifier=interface, qualifier=qualifier)

    def _find(self, identifier: NameOrInterface, qualifier: t.Any = None) -> t.Any:
        key = Container._get_registry_key(identifier, qualifier)
        try:
            registered_constructor = self._constructor_registry[key]
        except KeyError as e:
            raise DependencyNotFoundError(identifier=identifier, qualifier=qualifier) from e
        return self.get_object(*registered_constructor)

    def get_object(self, constructor: Constructor, kwargs: Kwargs = None) -> t.Any:
        """
        Gets proper scope type and creates instance of registered constructor accordingly.
        """
        kwargs = kwargs or {}
        scope_function = getattr(constructor, _SCOPE_TYPE_REF, self._default_scope)
        return scope_function(self, constructor, kwargs)

    def find_by_name(self, name: str, qualifier: t.Any = None) -> t.Any:
        """Finding registered constructors by name."""
        key = Container._get_registry_key(name, qualifier)
        try:
            registered_constructor = self._registry[key]
        except KeyError as e:
            raise DependencyNotFoundError(name=name, qualifier=qualifier) from e
        return self.get_object(*registered_constructor)

    def find_by_interface(self, interface: type, qualifier: t.Any = None) -> t.Any:
        """Finding registered constructors by interface."""
        key = Container._get_registry_key(interface, qualifier)
        try:
            registered_constructor = self._registry[key]
        except KeyError as e:
            raise DependencyNotFoundError(interface=interface, qualifier=qualifier) from e
        return self.get_object(*registered_constructor)

    def get_object(self, constructor: Constructor, kwargs: Kwargs = None) -> t.Any:
        """
        Gets proper scope type and creates instance of registered constructor accordingly.
        """
        kwargs = kwargs or {}
        scope_function = getattr(constructor, '__scope_type', self._default_scope)
        return scope_function(self, constructor, kwargs)

    # Implementation of the scopes

    def instance_scope(self, constructor: Constructor, kwargs: Kwargs) -> t.Any:
        """Every injection makes a new instance."""
        return constructor(self, **kwargs)

    def singleton_scope(self, constructor: Constructor, kwargs: Kwargs) -> t.Any:
        """First injection makes a new instance, later ones return the same instance."""
        try:
            instance = self._singleton_registry[constructor]
        except KeyError:
            instance = self._singleton_registry[constructor] = constructor(self, **kwargs)
        return instance


class Component:
    """
    Archetypal superclass for DI Component, i.e. a class that can be injected.

    The only expectation is (*) that it has to accept container as the first argument
    of its `__init__`. The Component may use container to have dependant components
    of its own, but this is not a requirement.

    Actual components may inherit from this class but they do not have to, as long as
    they comply with the (*) requirement.
    """
    def __init__(self, container: Container):
        self.container = container


class Scopes(Enum):
    INSTANCE: ScopeFunction = partial(Container.instance_scope)
    SINGLETON: ScopeFunction = partial(Container.singleton_scope)

    def __call__(self, container: Container, constructor: Constructor, kwargs: Kwargs):
        return self.value(container, constructor, kwargs)

    def __repr__(self):
        return f"<Scopes.{self.name}>"


def scope(scope_type: Scopes) -> t.Callable:
    def decorator(obj: t.Callable) -> t.Callable:
        obj.__scope_function = scope_type
        return obj
    return decorator


class Inject:
    """
    A descriptor for injecting dependencies as properties
    """

    container: Container = None
    type_: t.Type = None

    def __init__(self, name: str = None, interface: t.Type = None, qualifier: t.Any = None):
        self.name = name
        self.interface = interface
        self.qualifier = qualifier

    def __get__(self, instance: t.Any, owner: t.Type) -> t.Any:
        if instance is None:
            return self

        if self.container is None:
            self.container = instance.container

        return _find_object(
            self.container, self.name, self.interface or self.type_, self.qualifier
        )

    def __set_name__(self, owner: t.Type, name: str) -> None:
        self.type_ = owner.__annotations__.get(name) if hasattr(owner, '__annotations__') else None


def _find_object(container, name, interface, qualifier):
    if name:
        return container.find_by_name(name, qualifier)
    elif interface:
        return container.find_by_interface(interface, qualifier)
    else:
        raise TypeError('Missing name or interface for Inject.')


def inject(fun: t.Callable) -> t.Callable:
    """
    A decorator for injecting dependencies into methods,

    """
    signature = inspect.signature(fun)

    annotations: t.Dict[str, t.Any] = {}
    for name, param in signature.parameters.items():
        if name == 'self':
            continue
        else:
            default = param.default
            if isinstance(default, Inject):
                annotations[name] = (
                    param.annotation if param.annotation is not param.empty else None,
                    default
                )

    @wraps(fun)
    def wrapper(*args, **kwargs):
        container = getattr(args[0], 'container', None)

        if not container:
            raise ValueError('Container not provided.')

        for name_, data in annotations.items():
            if name_ not in kwargs:
                annotation, inject_instance = data
                kwargs[name_] = _find_object(
                    container,
                    inject_instance.name,
                    annotation or inject_instance.interface,
                    inject_instance.qualifier
                )

        return fun(*args, **kwargs)

    return wrapper
