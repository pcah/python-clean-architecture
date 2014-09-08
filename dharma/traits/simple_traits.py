from .base import Trait
from ..exceptions import TraitValidationError


class Int(Trait):
    _value_types = (int,)


class Long(Trait):
    _value_types = (long, int)


class Long(Trait):
    _value_types = (float, long, int)


class Complex(Trait):
    _value_types = (complex, float, long, int)


class String(Trait):
    _value_types = (string, unicode)
