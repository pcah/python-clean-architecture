from dataclasses import dataclass
import typing as t

from pca.data.validation import validated_by, Validator
from pca.exceptions import LogicError
from pca.utils.dependency_injection import container_supplier, inject
from pca.utils.functools import error_catcher, reify


Kwargs = t.Mapping[str, t.Any]
RequestModel = Kwargs


@dataclass(frozen=True)
class ResponseModel:
    data: Kwargs = None
    errors: Kwargs = None

    @reify
    def is_success(self):
        return not self.errors


# TODO #45. should InputPort & OutputPort be explicitly defined?
InputPort = t.Mapping[str, t.Any]
OutputPort = t.Callable[[ResponseModel], t.Any]
InteractorFunction = t.Callable[[RequestModel, t.Any], ResponseModel]


def interactor_factory(
    error_class: t.Union[t.Type[Exception], t.Sequence[t.Type[Exception]]] = LogicError,
    success_constructor: t.Callable = None,
    error_constructor: t.Callable = None,
):
    """
    Decorator factory that builds a decorator to enriches an application function
    with additional features:

    * input data will be validated using given validators
    * decorated function can use Inject descriptors in its signature
    * errors, described with `error_class`, raised during validation and interaction itself,
      will be turned into a result using `error_constructor`; successful results may
      be post-processed like the error ones, using `success_constructor`
    """
    def interactor(*validators: Validator):
        """
        Closure which encloses arguments of error handling. Takes series of validators
        as the arguments.

        :param validators: callables that make some validation; it might be instances of
            schemas or plain functions that make some additional validation; they should
            take the same signature as the decorated function, ie. may use injected
            dependencies
        :returns: container closure that returns decorated interactor
        """
        def decorator(f: InteractorFunction):
            """
            The actual decorator of an interactor function. Enwraps decorated with decorators
            of validation, error handling and dependency injection.
            """
            decorated_f = validated_by(*validators)(f)
            decorated_f = error_catcher(
                error_class=error_class,
                success_constructor=success_constructor,
                error_constructor=error_constructor
            )(decorated_f)
            decorated_f = inject(decorated_f)
            decorated_f = container_supplier(decorated_f)
            return decorated_f

        return decorator

    return interactor
