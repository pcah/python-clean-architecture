import inspect
from enum import Enum
from functools import partial, wraps
import typing as t

from pca.exceptions import ConfigError, ErrorCatalog
from pca.utils.collections import frozendict

NameOrInterface = t.Union[type, str]
Constructor = t.Union[t.Type, t.Callable]
Kwargs = t.Dict[str, t.Any]  # keyword-arguments of a Constructor
ScopeFunction = t.Callable[[Constructor, Kwargs], t.Any]

_SCOPE_TYPE_REF = '__di_scope_type__'


class DIErrors(ErrorCatalog):
    DEFINITION_NOT_FOUND = ConfigError(hint=(
        "A dependency definition for DI was tried to be injected, but it has not been found."))
    AMBIGUOUS_DEFINITION = ConfigError(hint="This identifier has already been registered.")
    NO_IDENTIFIER_SPECIFIED = ConfigError(hint="Missing both name and interface for Inject.")
    NO_CONTAINER_PROVIDED = ConfigError(
        hint="DI resolving found no instance of the DI `Container` to work with.")
    INTEGRATION_NOT_FOUND = ConfigError(hint=(
        "An integration target tried to use its external library, but it has not been found."))


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
            raise DIErrors.AMBIGUOUS_DEFINITION.with_params(
                identifier=identifier, qualifier=qualifier)
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
        except KeyError:
            raise DIErrors.DEFINITION_NOT_FOUND.with_params(
                identifier=identifier, qualifier=qualifier)
        return self.get_object(*registered_constructor)

    def get_object(self, constructor: Constructor, kwargs: Kwargs = None) -> t.Any:
        """
        Gets proper scope type and creates instance of registered constructor accordingly.
        """
        kwargs = kwargs or {}
        scope_function = getattr(constructor, _SCOPE_TYPE_REF, self._default_scope)
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


class Inject:
    """
    A class that can serve as:
    * a descriptor for a `Component` class
    * argument's default value
    that should be used to mark a place for injecting dependencies as an attribute or an argument
    of a function.
    """

    annotation: t.Type = None

    def __init__(self, name: str = None, interface: t.Type = None, qualifier: t.Any = None):
        self.name = name
        self.interface = interface
        self.qualifier = qualifier

    def __set_name__(self, owner: t.Type['Component'], name: str) -> None:
        self.annotation = owner.__annotations__.get(name) \
            if hasattr(owner, '__annotations__') else None

    def __get__(self, instance: t.Any, owner: t.Type) -> t.Any:
        if instance is None:
            return self
        return self.find(instance.container)

    def find(self, container: Container) -> t.Any:
        """
        Finds a injected instance of the dependency declared by the `Inject` attributes using
        given container.
        """
        return _find_dependency(
            container, self.name, self.interface or self.annotation, self.qualifier
        )


def _find_dependency(
        container: Container, name: str, interface: t.Type, qualifier: t.Any
) -> t.Any:
    """
    A helper function to prioritize name vs interface precedence & collision when seeking for
    a dependency.
    """
    if name:
        return container.find_by_name(name, qualifier)
    elif interface:
        return container.find_by_interface(interface, qualifier)
    else:
        raise DIErrors.NO_IDENTIFIER_SPECIFIED


class ComponentMeta(type):
    """
    A metaclass that gathers all `Inject` dependency markers in declaration of a class inheriting
    the `Component` class.
    """
    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        cls.__dependencies__ = frozendict(
            (k, v) for k, v in dict.items()
            if isinstance(v, Inject)
        )


class Component(metaclass=ComponentMeta):
    """
    Archetypal superclass for DI Component, i.e. a class that can be injected.

    The only expectation is that it has to accept container as the first argument
    of its `__init__`. The Component may use container to have dependant components
    of its own, but this is not a requirement.
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
    """
    A decorator for declaring DI scope for the constructor of a dependency: a class or a factory
    function. See `Scopes` enum for details of each scope type.

    :param scope_type: a scope enum to set for the decorated constructor
    """
    def decorator(obj: t.Callable) -> t.Callable:
        setattr(obj, _SCOPE_TYPE_REF, scope_type)
        return obj
    return decorator


def inject(f: t.Callable) -> t.Callable:
    """
    A decorator for injecting dependencies into functions. It looks for DI container
    either on the function itself or on its first argument (`self` when `f` is a method).
    """
    signature = inspect.signature(f)
    dependency_declarations: t.Dict[str, Inject] = {}

    for name, param in signature.parameters.items():
        default = param.default
        if isinstance(default, Inject):
            dependency_declarations[name] = default
            if param.annotation is not param.empty:
                default.interface = param.annotation

    @wraps(f)
    def wrapper(*args, **kwargs):
        # look for the DI container either on the function itself
        # or on its first argument (`self` when `f` is a method)
        container = getattr(wrapper, 'container', None) \
            or (getattr(args[0], 'container', None) if args else None)

        if not container:
            # noinspection PyUnresolvedReferences
            raise DIErrors.NO_CONTAINER_PROVIDED.with_params(
                module=f.__module__, function=f.__qualname__)

        # provide arguments that haven't been supplied by the call's kwargs
        for name_, dependency_declaration in dependency_declarations.items():
            if name_ not in kwargs:
                kwargs[name_] = dependency_declaration.find(container)

        # finally, the call with all the injected arguments
        return f(*args, **kwargs)

    wrapper.__dependencies__ = dependency_declarations
    return wrapper


T = t.TypeVar('T', t.Callable, t.Type[object], covariant=True)


def container_supplier(target: T) -> t.Callable[[Container], T]:
    """
    A decorator that produces a closure supplying a container instance into a component or
    a function. Target can be either a function to use with a `inject` decorator or a class
    which methods use `inject` decorator.
    """
    @wraps(target)
    def container_closure(container: Container) -> T:
        """A closure supplying a component or a function with a container instance."""
        target.container = container
        return target

    return container_closure
