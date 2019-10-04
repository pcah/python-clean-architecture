from dataclasses import dataclass
import typing as t

from pca.utils.collections import frozendict
from pca.utils.compat import GenericABCMeta

from .container import (
    Constructor,
    Container,
    DIContext,
    Kwargs,
    get_di_container,
    set_di_context,
)
from .descriptors import Inject

_DEPENDENCIES_REF = '__di_dependencies__'

AttributeContexts = t.Dict[str, DIContext]
MethodContexts = t.Dict[str, t.Sequence[DIContext]]
Injectable = t.TypeVar('Injectable', t.Callable, t.Type[object], covariant=True)


@dataclass(frozen=True)
class DIDependencies:
    """
    Describes relations between a Component subclass and all its dependencies.

    :cvar attribute_contexts: DI contexts of all attributes as a mapping
        {attribute_name: DIContext}
    :cvar method_contexts: DI contexts of all dependencies of all methods as a mapping
        {method_name: {argument_name: DIContext}}
    """
    attribute_contexts: AttributeContexts
    method_contexts: MethodContexts


def set_dependencies_contexts(
        instance: t.Any,
        attribute_contexts: AttributeContexts,
        method_contexts: MethodContexts
) -> None:
    """
    A helper function to create and set a description object for all dependencies of a Component.
    """
    setattr(instance, _DEPENDENCIES_REF, DIDependencies(
        frozendict(attribute_contexts), frozendict(method_contexts)
    ))


def get_dependencies_contexts(instance: t.Any) -> DIDependencies:
    """A helper function to extract description of all dependencies of a Component."""
    return getattr(instance, _DEPENDENCIES_REF, None)


def get_attribute_dependencies(instance: t.Any) -> t.Dict[str, t.Any]:
    """A helper function to extract dependencies of all attribute dependencies of a Component."""
    description = get_dependencies_contexts(instance)
    if not description:
        return {}
    container = get_di_container(instance)
    return {
        name: context.get(container)
        for name, context in description.attribute_contexts.items()
    }


class ComponentMeta(GenericABCMeta):
    """
    A metaclass that gathers all dependency markers (from its attributes and methods)
    in a describing data class.
    """
    def __init__(cls, name, bases, d, **kwargs):
        # noinspection PyArgumentList
        super().__init__(name, bases, d, **kwargs)
        attribute_contexts: t.Dict[str, DIContext] = {
            k: v.context
            for k, v in d.items()
            if isinstance(v, Inject)
        }
        method_contexts: t.Dict[str, t.Sequence[DIContext]] = {
            k: v
            for k, v in d.items()
            if hasattr(v, _DEPENDENCIES_REF)
        }
        set_dependencies_contexts(cls, attribute_contexts, method_contexts)


class Component(metaclass=ComponentMeta):
    """
    A mixin superclass for DI Component, i.e. a class that can be injected and can have
    injectable
    """


def create_component(
    constructor: Constructor,
    container: Container,
    context: DIContext = None,
    kwargs: Kwargs = None,
) -> Component:
    """
    A helper function to create component respecting its relation to DI container & DI context.
    """
    context = context or DIContext()
    instance: Component = constructor(**(kwargs or {}))
    set_di_context(instance, container, context)
    return instance
