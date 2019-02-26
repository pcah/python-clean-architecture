# -*- coding: utf-8 -*-
import typing as t
from functools import update_wrapper, wraps

from .imports import get_dotted_path


# noinspection PyPep8Naming
class reify(object):  # noqa: N801
    """
    Taken from pyramid.decorator.

    Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the method it
    decorates into the instance dict after the first call, effectively
    replacing the function it decorates with an instance variable.  It is, in
    Python parlance, a non-data descriptor.  The following is an example and
    its usage:

    .. doctest::

        >>> from pyramid.decorator import reify

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

    def __init__(self, wrapped):
        self.wrapped = wrapped
        update_wrapper(self, wrapped)

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        inst.__dict__[self.wrapped.__name__] = val
        return val


def error_catcher(
        error_class: t.Union[t.Type[Exception], t.Sequence[t.Type[Exception]]] = Exception,
        success_constructor: t.Callable = None,
        error_constructor: t.Callable = None,
):
    """
    Catches expected type(s) of errors from a callable. Can process successful result
    or an error instance iff appropriate callback has been provided.

    :param error_class: a class of errors or a tuple of classes to be caught.
    :param success_constructor: a callable that can process successful result.
    :param error_constructor: a callable that can process erroneous result.
    :returns:
        * normal reply or a processed successful result iff calling the function has completed
          with success
        * an error instance or a processed erroneous result iff calling the function has raised
          an error instance of specified type(s)
    """
    success_constructor = success_constructor or (lambda result, **kwargs: result)
    error_constructor = error_constructor or (lambda error, **kwargs: error)

    def decorator(f: t.Callable):

        function_name = get_dotted_path(f)

        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
            except error_class as e:
                result = error_constructor(
                    error=e,
                    function_name=function_name,
                    args=args,
                    kwargs=kwargs
                )
            else:
                result = success_constructor(
                    result=result,
                    function_name=function_name,
                    args=args,
                    kwargs=kwargs
                )
            return result

        return wrapper

    return decorator
