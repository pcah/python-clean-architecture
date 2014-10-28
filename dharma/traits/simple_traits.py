import six

from .base import Trait
from ..exceptions import TraitValidationError


class Int(Trait):
    _value_types = (int,)


class Float(Trait):
    _value_types = (int,)


class Long(Trait):
    _value_types = six.integer_types


class Long(Trait):
    _value_types = (float,) + six.integer_types


class Complex(Trait):
    _value_types = (complex, float) + six.integer_types


class Text(Trait):
    """
    """
    _value_types = six.string_types
