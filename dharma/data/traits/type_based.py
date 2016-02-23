import abc

from .base import Trait
from ..exceptions import TraitValidationError
from .predicates import Predicate


_CAST_TYPE_ERROR = (
    "Trait sanity test: you're trying to use a casting trait without "
    "correctly specifying the casting type.")


class TypeBasedTrait(Trait):
    """
    Base class for Traits which validation base on a
    """

    def __init__(self, genus, diff=None, cast=False):
        """
        Params:
            genus --
            validators - iterable of (value, Nature) -> None functions that
                are called when Trait changes its value. They are supposed
                to raise `TraitValidationError` if they consider value to be
                invalid. Nature argument is given for the sake of cross-trait
                validation on Nature instance. Validators are supported
                on per-Nature-class basis.
            cast -- a boolean describing whether value assigned to the trait
                should be casted to the expected type of value. Casting is done
                before validation. Default: False
        """
        super(TypeBasedTrait, self).__init__()
        self._genus = genus
        self._accepted_types = (genus,)
        self._diff = diff if isinstance(diff, Predicate) else Predicate(diff)
        self._cast = cast
        self._cast_to = None

    def cast(self, value):
        """
        Casts new value to the type specified by `_cast_to` attribute.
        Can be used as a hook for more sophisticated logic.

        Param:
            value -- value to be cast.

        Returns:
            casted value.
        """
        assert self._cast_to, _CAST_TYPE_ERROR
        return self._cast_to(value)

    @abc.abstractproperty
    def _accepted_types(self):
        """
        """

    def validate(self, value):
        """
        """
        if not isinstance(value, self._accepted_types):
            msg = "Invalid type of value: was {}; should be: {}".format(
                type(value), self._value_types)
            raise TraitValidationError(msg)
        if self._diff:
            self._diff(value)

    def validate_value(self, value):
        """
        Validates a value to be assigned. If overridden to introduce custom
        validation, it should call its super version or take the responsibility
        of calling each of `self.validators`.

        Params:
            value - a value to be verified.

        Raises:
            TraitValidationError - when the value isn't one of `_value_types`
            or doesn't conform one of validators.
        """
        for validator in self.validators:
            try:  # TODO how to call?
                validator(value, self._instance)
            except TypeError:
                # case: only value
                validator(value)
