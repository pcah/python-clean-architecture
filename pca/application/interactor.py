from dataclasses import dataclass
import typing as t

from pca.data.validation import validated_by, Validator
from pca.utils.dependency_injection import container_supplier, inject
from pca.utils.functools import reify


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


def interactor_function(*validators: Validator):
    """
    Decorator factory that enriches an interactor function with additional features:

    * input data will be validated using given schema and validators (look bellow)
    * decorated function can use Inject descriptors in its signature
    * TODO #4 every error raised will be turned into an ResponseModel

    :param validators: callables that make some validation; it might be instances of
        schemas or plain functions that make some additional validation; they should
        take the same signature as the decorated function, ie. may use injected
        dependencies
    :return: container closure that returns decorated interactor
    """
    def decorator(f: InteractorFunction):
        decorated_f = validated_by(*validators)(f)
        decorated_f = inject(decorated_f)
        decorated_f = container_supplier(decorated_f)
        return decorated_f

    return decorator
