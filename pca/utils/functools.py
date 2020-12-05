import typing as t

from functools import wraps

from .compat import singledispatchmethod  # noqa: F401 backported to this repo
from .imports import get_dotted_path


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
                    error=e, function_name=function_name, args=args, kwargs=kwargs
                )
            else:
                result = success_constructor(
                    result=result, function_name=function_name, args=args, kwargs=kwargs
                )
            return result

        return wrapper

    return decorator
