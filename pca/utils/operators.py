import six
import typing as t

from pca.exceptions import PathNotFoundError
from pca.utils.exceptions import catch_warning


def resolve_path(path: t.Iterable[str]) -> t.Callable[..., t.Any]:
    # raises: PathNotFoundError
    def resolve_path_curried(value):
        for part in path:
            try:
                value = value[part]
            except (KeyError, TypeError):
                try:
                    value = getattr(value, part)
                except AttributeError:
                    raise PathNotFoundError
        return value

    return resolve_path_curried


def check_path(
    test: t.Callable[[t.Any, t.Any], bool],
    path: t.Iterable[str]
) -> t.Callable[..., bool]:
    def check_path_curried(value):
        orig_value = value
        for part in path:
            try:
                value = getattr(value, part)
            except AttributeError:
                try:
                    value = value[part]
                except (KeyError, TypeError):
                    return False
        return test(value, orig_value)

    return check_path_curried


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


def error_catcher(
        error_class: t.Union[t.Type[Exception], t.Sequence[Exception]],
        func: t.Callable[..., t.Any],
        *args,
        **kwargs
):
    """
    Catches expected type(s) of errors from a callable.

    :param error_class: a class of errors or a tuple of classes to be caught
    :param func: a callable that is expected to raise (one of) `error_class` errors
    :return: a boolean that shows iff error was caught
    """
    try:
        func(*args, **kwargs)
        return True
    except error_class:
        return False
