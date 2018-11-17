# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import enum
import re

from pca.exceptions import TraitValidationError


def construct_validators(genus):
    return ()


class ValidationErrorCode(enum.Enum):
    MIN_LENGTH = 'MIN_LENGTH'
    MAX_LENGTH = 'MAX_LENGTH'
    MIN_VALUE = 'MIN_VALUE'
    MAX_VALUE = 'MAX_VALUE'
    REGEX_MISMATCH = 'REGEX_MISMATCH'
    IP_MISMATCH = 'IP_MISMATCH'
    ELEMENT_MISMATCH = 'ELEMENT_MISMATCH'
    EMAIL_MISMATCH = 'EMAIL_MISMATCH'


def min_length(limit):
    # type: (numbers.Number) -> Validator
    return Validator(
        name='min_length',
        test=lambda value: len(value) > limit,
        code=ValidationErrorCode.MIN_LENGTH,
        limit=limit,
    )


def max_length(limit):
    # type: (numbers.Number) -> Validator
    return Validator(
        name='max_length',
        test=lambda value: len(value) < limit,
        code=ValidationErrorCode.MAX_LENGTH,
        limit=limit,
    )


def min_value(limit):
    # type: (numbers.Number) -> Validator
    return Validator(
        name='min_value',
        test=lambda value: value > limit,
        code=ValidationErrorCode.MIN_VALUE,
        limit=limit,
    )


def max_value(limit):
    # type: (numbers.Number) -> Validator
    return Validator(
        name='max_value',
        test=lambda value: value < limit,
        code=ValidationErrorCode.MAX_VALUE,
        limit=limit,
    )


def elements_belong_to(container, error_code=ValidationErrorCode.ELEMENT_MISMATCH):  # flake8: noqa
    # type: (collections.Container, six.text_type) -> Validator
    return Validator(
        name='check_elements',
        test=lambda value: all(e in value for e in container),
        code=error_code,
        elements=container,
    )


def regex(pattern, flags=0, error_code=ValidationErrorCode.REGEX_MISMATCH):
    # type: (six.text_type, int, six.text_type) -> Validator
    re_object = re.compile(pattern, flags=flags)
    return Validator(
        name='regex',
        test=lambda value: bool(re_object.match(value)),
        code=error_code,
        pattern=pattern,
        flags=flags,
    )


EMAIL_USER_RE = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
    re.IGNORECASE)
EMAIL_DOMAIN_RE = re.compile(
    # max length for domain name labels is 63 characters per RFC 1034
    r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z',
    re.IGNORECASE)
EMAIL_LITERAL_RE = re.compile(
    # literal form, ipv4 or ipv6 address (SMTP 4.1.3)
    r'\[([A-f0-9:\.]+)\]\Z',
    re.IGNORECASE)


def email_validator(value, whitelist):
    # value = force_text(value)

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


def email(whitelist=None, error_code=ValidationErrorCode.EMAIL_MISMATCH):
    # type: (collections.Container, six.text_type) -> Validator
    whitelist = whitelist or ('localhost',)
    return Validator(
        name='ip',
        test=lambda value: email_validator(value, whitelist),
        code=error_code,
        whitelist=whitelist,
    )


IPv4_RE = re.compile(r'^(?:(?:2[0-4]\d|25[0-5]|1\d{2}|[1-9]?\d)\.){3}(?:2[0-4]\d|25[0-5]|1\d{2}|[1-9]?\d)$')


def ip4(whitelist=None, error_code=ValidationErrorCode.IP_MISMATCH):
    # type: (collections.Container, six.text_type) -> Validator
    whitelist = whitelist or ('localhost',)
    return Validator(
        name='ip',
        test=lambda value: value in whitelist or bool(IPv4_RE.match(value)),
        code=error_code,
        whitelist=whitelist,
    )


class Validator(object):
    """
    Represents named validator, parametrized by test, error code
    """
    name = None
    test = None
    kwargs = None
    code = None

    def __init__(self, name, test, code=None, **kwargs):
        # type: (basestring, Callable[[Any], bool], basestring, **Any) -> None
        self.name = name or hex(id((test, kwargs)))
        self.test = test
        self.kwargs = kwargs
        if code:
            self.code = code

    def __call__(self, value):
        if not self.test(value, **self.kwargs):
            raise TraitValidationError(code=self.code)

    def __repr__(self):
        return "<{}: {}>".format(
            self.__class__.__name__,
            self.name,
            self.kwargs
        )
