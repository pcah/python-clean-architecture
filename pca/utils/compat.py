import os
from abc import ABCMeta


PY36 = (3, 6) <= os.sys.version_info < (3, 7)


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
