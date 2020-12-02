from functools import wraps
import inspect
import typing as t

from .container import (
    Container,
    Constructor,
    DIContext,
    Scopes,
    get_di_container,
    set_di_context,
    set_scope_type,
)
from .component import Injectable, set_dependencies_contexts
from .descriptors import Inject
from .errors import DIErrors


def scope(scope_type: Scopes) -> t.Callable[[Constructor], Constructor]:
    """
    A decorator for declaring DI scope for the constructor of a dependency: a class or a factory
    function. See `Scopes` enum for details of each scope type.

    :param scope_type: a scope enum to set for the decorated constructor
    """

    def decorator(constructor: Constructor) -> Constructor:
        set_scope_type(constructor, scope_type)
        return constructor

    return decorator


def inject(f: Injectable) -> Injectable:
    """
    A decorator for injecting dependencies into functions. It looks for DI container
    either on the function itself or on its first argument (`self` when `f` is a method).
    """
    signature = inspect.signature(f)
    dependency_declarations: t.Dict[str, DIContext] = {}

    for name, param in signature.parameters.items():
        default = param.default
        if isinstance(default, Inject):
            dependency_declarations[name] = default.context
            if param.annotation is not param.empty:
                object.__setattr__(default.context, "interface", param.annotation)

    @wraps(f)
    def wrapper(*args, **kwargs):
        # look for the DI container either on the function itself
        # or on its first argument (`self` when `f` is a method)
        container = get_di_container(wrapper) or (get_di_container(args[0]) if args else None)

        if not container:
            # noinspection PyUnresolvedReferences
            raise DIErrors.NO_CONTAINER_PROVIDED.with_params(
                module=f.__module__, function=f.__qualname__
            )

        # provide arguments that haven't been supplied by the call's kwargs
        for name_, dependency_declaration in dependency_declarations.items():
            if name_ not in kwargs:
                kwargs[name_] = dependency_declaration.get(container)

        # finally, the call with all the injected arguments
        return f(*args, **kwargs)

    set_dependencies_contexts(
        wrapper, attribute_contexts=dependency_declarations, method_contexts={}
    )
    return wrapper


def container_supplier(target: Injectable) -> t.Callable[[Injectable], Injectable]:
    """
    A decorator that produces a closure supplying a container instance into a component or
    a function. Target can be either a function to use with a `inject` decorator or a class
    which methods use `inject` decorator.
    """

    @wraps(target)
    def container_closure(container: Container, context: DIContext = None) -> Injectable:
        """A closure supplying a component or a function with a container instance."""
        set_di_context(target, container, context)
        return target

    return container_closure
