import typing as t

from pca.exceptions import PathNotFoundError


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


def error_catcher(
        error_class: t.Union[t.Type[Exception], t.Sequence[t.Type[Exception]]],
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
