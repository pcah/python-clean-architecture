import typing as t

from dataclasses import (
    InitVar,
    dataclass,
    field,
)

from .container import (
    DIContext,
    get_di_container,
)
from .errors import (
    ConfigError,
    DIErrors,
)


@dataclass(frozen=True)
class Inject:
    """
    A class that can serve as:
        * a descriptor for a `Component` class
        * a default value of a function argument
    that should be used to mark a place for injecting dependencies as an attribute or an argument
    of a function.
    """

    context: DIContext = field(init=False)
    name: InitVar[str] = None
    interface: InitVar[t.Type] = None
    qualifier: InitVar[t.Any] = None
    get_qualifier: InitVar[t.Callable[[t.Any], t.Any]] = None

    label: str = None
    annotation: t.Type = None

    def __post_init__(
        self,
        name: str,
        interface: t.Type,
        qualifier: t.Any,
        get_qualifier: t.Callable[[t.Any], t.Any] = None,
    ):
        object.__setattr__(
            self,
            "context",
            DIContext(
                name=name, interface=interface, qualifier=qualifier, get_qualifier=get_qualifier
            ),
        )

    def __set_name__(self, owner, name: str) -> None:
        annotation = owner.__annotations__.get(name) if hasattr(owner, "__annotations__") else None
        # supporting object's immutability
        object.__setattr__(self, "label", name)
        if annotation:
            object.__setattr__(self.context, "interface", annotation)

    def __get__(self, instance: t.Any, owner: t.Type) -> t.Any:
        if instance is None:
            return self
        container = get_di_container(instance)
        if not container:
            raise DIErrors.NO_CONTAINER_PROVIDED.with_params(
                class_name=instance.__class__.__qualname__, attribute=self.label
            )
        context = self.context.determine(instance)
        try:
            return context.get(container=container)
        except ConfigError as e:
            raise e.with_params(
                class_name=instance.__class__.__qualname__,
                attribute=self.label,
                context=e.params.get("context"),
            )
