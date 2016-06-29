import six
from typing import (  # noqa
    Any,
    Callable,
    Iterable,
)

from dharma.utils.exceptions import catch_warning


def resolve_path(
        test,  # type: Callable[[Any], bool]
        path,  # type: Iterable[str]
):  # type: (...) -> Callable[..., bool]
    def resolve_path_curried(value):
        for part in path:
            try:
                value = getattr(value, part)
            except AttributeError:
                try:
                    value = value[part]
                except (KeyError, TypeError):
                    return False
        return test(value)

    return resolve_path_curried


if six.PY2:  # pragma: no cover
    # noinspection PyUnresolvedReferences
    def eq(value, rhs):
        """
        Comparision function with UTF-8 handling on unicode vs str comparation
        on Python 2
        """
        with catch_warning(UnicodeWarning):
            try:
                return value == rhs
            except UnicodeWarning:
                # Dealing with a case, where 'value' or 'rhs'
                # is unicode and the other is a byte string.
                if isinstance(value, str):
                    return value.decode('utf-8') == rhs
                elif isinstance(rhs, str):
                    return value == rhs.decode('utf-8')
                else:
                    raise TypeError()

else:  # pragma: no cover
    def eq(value, rhs):
        """Plain ol' __eq__ compare."""
        return value == rhs
