from dataclasses import dataclass
from enum import Enum
from functools import partial
import typing as t

from .errors import DIErrors

NameOrInterface = t.Union[type, str]
Constructor = t.Union[t.Type, t.Callable]
Kwargs = t.Dict[str, t.Any]  # keyword-arguments of a Constructor
ScopeFunction = t.Callable[[Constructor, Kwargs], t.Any]

_CONTAINER_REF = '__di_container__'
_CONTEXT_REF = '__di_context__'
_SCOPE_TYPE_REF = '__di_scope__'


@dataclass(frozen=True)
class DIContext:
    """
    Describes the way a component might be requested from the Container.

    :cvar name: an arbitrary string describing dependency, but it doesn't give any
        information about its interface
    :cvar interface: (an alternative to `name` argument) an interface of the dependency;
        often used along with annotations about the variable/argument that requests the dependency
    :cvar qualifier: an object of any type that adds a finer grade granularity about
        the dependency; i.e. you may want a component of `IDao` interface: not just anyone, but
        the one that is modeling some specific schema; the qualifier describes the latter
        condition.
    """
    name: str = None
    interface: t.Type = None
    qualifier: t.Any = None

    def get(self, container: 'Container') -> t.Any:
        """
        Finds a injected instance of the dependency declared by the `Inject` attributes using
        given container. Prioritizes name vs. interface precedence & collision when seeking for
        a dependency.
        """
        if self.name:
            return container.find_by_name(self.name, self.qualifier)
        elif self.interface:
            return container.find_by_interface(self.interface, self.qualifier)
        else:
            raise DIErrors.NO_IDENTIFIER_SPECIFIED


@dataclass(frozen=True)
class DIResolution:
    """
    Describes what has been registered as a dependency:

    :cvar constructor: a type or a callable that builds the dependency instance
    :cvar kwargs: a kwargs dict that specifies keyword arguments for the dependency constructor
    """
    constructor: Constructor
    kwargs: Kwargs = None


class Container:
    """
    Dependency Injection container. It is the basic object in the Dependency Injection mechanism
    and makes all the components use DI machinery for its own purposes.
    """

    def __init__(self, default_scope: 'Scopes' = None):
        self._constructor_registry: t.Dict[DIContext, DIResolution] = {}
        self._singleton_registry = {}
        self._default_scope = default_scope

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
        context = DIContext(name=name, qualifier=qualifier)
        self._register(
            context=context, constructor=constructor, kwargs=kwargs, scope=scope
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
        context = DIContext(interface=interface, qualifier=qualifier)
        # TODO Refs #20: should I register superclasses of the interface as well?
        self._register(
            context=context, constructor=constructor, kwargs=kwargs, scope=scope
        )

    def _register(
        self,
        context: DIContext,
        constructor: Constructor,
        kwargs: Kwargs = None,
        scope: 'Scopes' = None,
    ):
        """Technical detail of registering a constructor"""
        if context in self._constructor_registry:
            raise DIErrors.AMBIGUOUS_DEFINITION.with_params(context=context)
        self._constructor_registry[context] = DIResolution(constructor=constructor, kwargs=kwargs)
        if scope is not None:
            setattr(constructor, _SCOPE_TYPE_REF, scope)

    def find_by_name(self, name: str, qualifier: t.Any = None) -> t.Any:
        """Finding registered constructor by name."""
        return self._find(DIContext(name=name, qualifier=qualifier))

    def find_by_interface(self, interface: type, qualifier: t.Any = None) -> t.Any:
        """Finding registered constructor by interface."""
        # TODO Refs #20: should I look for the subclasses of the interface as well?
        return self._find(DIContext(interface=interface, qualifier=qualifier))

    def _find(self, context: DIContext) -> t.Any:
        try:
            resolution = self._constructor_registry[context]
        except KeyError:
            raise DIErrors.DEFINITION_NOT_FOUND.with_params(context=context)
        return self.get_object(resolution, context)

    def get_object(self, resolution: DIResolution, context: DIContext = None) -> t.Any:
        """
        Gets proper scope type and creates instance of registered constructor accordingly.
        """
        kwargs = resolution.kwargs or {}
        constructor = resolution.constructor
        context = context or DIContext()
        scope_function = get_scope_type(constructor) or self._default_scope
        return scope_function(self, constructor, kwargs, context)

    # Implementation of the scopes

    def instance_scope(
            self,
            constructor: Constructor,
            kwargs: Kwargs,
            context: DIContext = None
    ) -> t.Any:
        """Every injection makes a new instance."""
        instance = constructor(**kwargs)
        set_di_context(instance, self, context)
        return instance

    def singleton_scope(
            self,
            constructor: Constructor,
            kwargs: Kwargs,
            context: DIContext
    ) -> t.Any:
        """First injection makes a new instance, later ones return the same instance."""
        try:
            instance = self._singleton_registry[constructor]
        except KeyError:
            instance = self._singleton_registry[constructor] = constructor(**kwargs)
            set_di_context(instance, self, context)
        return instance


class Scopes(Enum):
    INSTANCE: ScopeFunction = partial(Container.instance_scope)
    SINGLETON: ScopeFunction = partial(Container.singleton_scope)

    def __call__(
            self,
            container: Container,
            constructor: Constructor,
            kwargs: Kwargs,
            context: DIContext = None,
    ) -> t.Any:
        return self.value(container, constructor, kwargs, context)

    def __repr__(self):
        return f"<Scopes.{self.name}>"


def set_di_context(instance: t.Any, container: Container, context: DIContext) -> None:
    """
    A helper function to set DI container & DI context to an arbitrary object to conform
    Dependency Injection mechanics.
    """
    # supporting immutable instances
    object.__setattr__(instance, _CONTAINER_REF, container)
    object.__setattr__(instance, _CONTEXT_REF, context)


def get_di_container(instance: t.Any) -> Container:
    """
    A helper function to extract the container from an arbitrary object that can serve as
    a component.
    """
    return getattr(instance, _CONTAINER_REF, None)


def get_di_context(instance: t.Any) -> DIContext:
    """
    A helper function to get from an arbitrary object its DI context.
    """
    return getattr(instance, _CONTEXT_REF, None)


def get_scope_type(constructor: Constructor) -> t.Optional[Scopes]:
    """
    A helper function to extract the scope type from a constructor.
    """
    return getattr(constructor, _SCOPE_TYPE_REF, None)


def set_scope_type(constructor: Constructor, scope: Scopes) -> None:
    """
    A helper function to set the scope type on a constructor.
    """
    setattr(constructor, _SCOPE_TYPE_REF, scope)
