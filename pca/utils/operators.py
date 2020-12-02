import typing as t


class PredicatePathNotFoundError(Exception):
    """Resolving a query predicate found object has no appropriate path."""


def resolve_path(path: t.Iterable[str]) -> t.Callable[..., t.Any]:
    # raises: PredicatePathNotFoundError
    def resolve_path_curried(value):
        for part in path:
            try:
                value = value[part]
            except (KeyError, TypeError):
                try:
                    value = getattr(value, part)
                except AttributeError:
                    raise PredicatePathNotFoundError
        return value

    return resolve_path_curried


def check_path(
    test: t.Callable[[t.Any, t.Any], bool], path: t.Iterable[str]
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
