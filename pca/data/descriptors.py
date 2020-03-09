from functools import update_wrapper
import typing as t

from pca.data.values import Value, Owner
from pca.utils.collections import freeze


# noinspection PyPep8Naming
class reify:  # noqa: N801
    """
    Taken from `pyramid.decorator`.

    Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the method it
    decorates into the instance dict after the first call, effectively
    replacing the function it decorates with an instance variable.  It is, in
    Python parlance, a non-data descriptor.  The following is an example and
    its usage:

    >>> class Foo(object):
    ...     @reify
    ...     def jammy(self):
    ...         print('jammy called')
    ...         return 1

    >>> f = Foo()
    >>> v = f.jammy
    jammy called
    >>> print(v)
    1
    >>> f.jammy
    1
    >>> # jammy func not called the second time; it replaced itself with 1
    >>> # Note: reassignment is possible
    >>> f.jammy = 2
    >>> f.jammy
    2
    """

    def __init__(self, wrapped: t.Callable):
        self.wrapped = wrapped
        update_wrapper(self, wrapped)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        val = self.wrapped(instance)
        instance.__dict__[self.wrapped.__name__] = val
        return val


def __not_supported__(name: str, instance: Owner) -> None:
    raise TypeError(
        f"An attribute '{name}' of class {instance.__class__.__name__} is immutable and can't be"
        f"modified."
    )


# noinspection PyPep8Naming
class frozen(t.Generic[Value]):

    owner: t.Any
    name: str
    _value_key: str
    # pattern for __dict__ key on the owner class; space chars are intended
    # to be sure we are not colliding with any proper attribute name
    _key_pattern = "'%s' frozen value"

    def __set_name__(self, owner: t.Any, name: str) -> None:
        self.owner = owner
        self.name = name
        self._value_key = self._key_pattern % self.name

    def __get__(self, instance: Owner, owner: t.Type) -> Value:
        if instance is None:
            return self
        try:
            value = instance.__dict__[self._value_key]
        except KeyError:
            __not_supported__(self.name, instance)
        return value

    def __set__(self, instance: Owner, value: Value) -> None:
        try:
            old_value = instance.__dict__[self._value_key]
        except KeyError:
            instance.__dict__[self._value_key] = freeze(value)
        else:
            if value != old_value:
                __not_supported__(self.name, instance)
