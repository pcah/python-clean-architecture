import os

from abc import ABCMeta
from functools import (
    singledispatch,
    update_wrapper,
)


PY36 = (3, 6) <= os.sys.version_info < (3, 7)
PY37 = (3, 7) <= os.sys.version_info < (3, 8)


if PY36:  # pragma: no cover
    from typing import GenericMeta

    class GenericABCMeta(GenericMeta, ABCMeta):
        """
        A compatibility class that solves the problem with metaclass conflict on mixing ABC
        with typing.Generic. Necessary only in Python 3.6 (in 3.7+ Generic class has
        no non-trivial metaclass.
        Ref: https://github.com/python/typing/issues/449
        """


else:  # pragma: no cover

    class GenericABCMeta(ABCMeta):
        pass


if PY36 or PY37:
    # Python 3.8 singledispatchmethod, backported
    class singledispatchmethod:
        """Single-dispatch generic method descriptor.

        Supports wrapping existing descriptors and handles non-descriptor
        callables as instance methods.
        """

        def __init__(self, func):
            if not callable(func) and not hasattr(func, "__get__"):
                raise TypeError(f"{func!r} is not callable or a descriptor")  # pragma: no cover
            self.dispatcher = singledispatch(func)
            self.func = func

        def register(self, cls, method=None):
            """generic_method.register(cls, func) -> func

            Registers a new implementation for the given *cls* on a *generic_method*.
            """
            return self.dispatcher.register(cls, func=method)

        def __get__(self, obj, cls=None):
            def _method(*args, **kwargs):
                method = self.dispatcher.dispatch(args[0].__class__)
                return method.__get__(obj, cls)(*args, **kwargs)

            _method.__isabstractmethod__ = self.__isabstractmethod__
            _method.register = self.register
            update_wrapper(_method, self.func)
            return _method

        @property
        def __isabstractmethod__(self):
            return getattr(self.func, "__isabstractmethod__", False)


else:
    from functools import singledispatchmethod  # pragma: no cover
assert singledispatchmethod
