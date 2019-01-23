import abc
import re
import typing as t
from functools import wraps

from pca.exceptions import TraitValidationError


Data = t.Mapping[str, t.Any]
Validator = t.Callable[[Data], Data]


class ISchema(abc.ABC):
    """
    An interface of the adapter for negotiating the interface of different validation
    libraries.
    """

    @abc.abstractmethod
    def __call__(self, input_data: Data) -> Data:
        """Performs validation on the given data."""
        raise NotImplementedError


def validated_by(*validators: Validator):
    """
    A decorator factory that enriches a function with validation capabilities.
    Validators can be any callable of signature of (Data) -> Data.
    They can be made from any validation schemas that validates data field by field
    or in cross-field manner. They can also represent ad-hoc checks of
    non-field-related validation logic. Sometimes it might be more convenient to
    write a single function that to write a schema with additional custom method.

    Validators can (but doesn't have to) process data (eg. interpret, cast, deserialize)
    and each output data of one validator (if there is any) will be passed to the next one and,
    finally, to the decorated function itself. If a validator doesn't return anything,
    next function will get the same input.
    """

    def decorator(f):

        @wraps(f)
        def decorated(input_data: Data, *args, **kwargs) -> Data:
            """
            Decorator that represents original method preceded by series of validation
            checks and possible data preprocessing by given validators, sequentially.
            """
            validated_data = input_data
            for validator in validators:
                result = validator(validated_data)
                # validator is eligible to alter input data for the decorated function
                # but doesnt have to; if it returns no result, his input will be used
                validated_data = validated_data if result is None else result
            # finally, calling the decorated function with the validated data
            return f(validated_data, *args, **kwargs)

        # TODO #39. expose InputPort (whatever it is), not `validators`
        decorator.validators = validators
        return decorated

    return decorator


EMAIL_USER_RE = re.compile(
    # dot-atom
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"
    # quoted-string
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',
    re.IGNORECASE
)
EMAIL_DOMAIN_RE = re.compile(
    # max length for domain name labels is 63 characters per RFC 1034
    r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z',
    re.IGNORECASE
)
EMAIL_LITERAL_RE = re.compile(
    # literal form, ipv4 or ipv6 address (SMTP 4.1.3)
    r'\[([A-f0-9:\.]+)\]\Z',
    re.IGNORECASE
)


def validate_domain_part(value):
    pass


def validate_email(value, whitelist):
    if not value or '@' not in value:
        raise TraitValidationError(code='MALFORMED_EMAIL')

    user_part, domain_part = value.rsplit('@', 1)

    if not EMAIL_USER_RE.match(user_part):
        raise TraitValidationError(code='MALFORMED_EMAIL')

    if (domain_part not in whitelist and
            not validate_domain_part(domain_part)):
        # Try for possible IDN domain-part
        try:
            domain_part = domain_part.encode('idna').decode('ascii')
            if validate_domain_part(domain_part):
                return
        except UnicodeError:
            pass
        raise TraitValidationError(code='MALFORMED_EMAIL')


IPv4_RE = re.compile(
    r'^(?:(?:2[0-4]\d|25[0-5]|1\d{2}|[1-9]?\d)\.){3}(?:2[0-4]\d|25[0-5]|1\d{2}|[1-9]?\d)$')
