# -*- coding: utf-8 -*-
import datetime as dt
import six
from typing import (  # noqa
    Any,
    Callable,
    Container,
    Iterable,
    List,
)

from .trait import Trait
from . import validation


def integer(min_value=None, max_value=None, validators=None, **kwargs):
    # type: (int, int, Iterable[Callable[[Any], bool]], **Any) -> Trait
    _validators = []  # type: List[Callable[[Any], bool]]
    if min_value is not None:
        _validators.append(validation.min_value(min_value))
    if max_value is not None:
        _validators.append(validation.max_value(max_value))
    if validators:
        _validators.extend(validators)
    return Trait(six.text_type, validators=tuple(_validators), **kwargs)


def string(min_length=None, max_length=None, chars=None, validators=None, **kwargs):
    # type: (int, int, collections.Container, Iterable[Callable[[Any], bool]], **Any) -> Trait
    _validators = []  # type: List[Callable[[Any], bool]]
    if min_length is not None:
        _validators.append(validation.min_length(min_length))
    if max_length is not None:
        _validators.append(validation.max_length(max_length))
    if chars is not None:
        _validators.append(validation.elements_belong_to(chars, code=validation.ValidationErrorCode))
    if validators:
        _validators.extend(validators)
    return Trait(six.text_type, validators=tuple(_validators), **kwargs)


def email(whitelist=None, validators=None, **kwargs):
    # type: (Container[six.text_type], Container[Callable[[Any], bool]], **Any) -> Trait
    _validators = (validation.email(whitelist=whitelist),)  # type: Iterable[Callable[[Any], bool]]
    if validators:
        _validators += validators
    return Trait(six.text_type, validators=_validators, **kwargs)


def ip4(whitelist=None, validators=None, **kwargs):
    # type: (Container[six.text_type], Iterable[Callable[[Any], bool]], **Any) -> Trait
    _validators = (validation.ip4(whitelist=whitelist),)  # type: Iterable[Callable[[Any], bool]]
    if validators:
        _validators += validators
    return Trait(six.text_type, validators=_validators, **kwargs)


def datetime(**kwargs):
    return Trait(dt.datetime, **kwargs)


def date(**kwargs):
    return Trait(dt.date, **kwargs)


def time(validators, **kwargs):
    return Trait(dt.time, **kwargs)
