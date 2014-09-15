import six

from ..exceptions import TraitInstantiationError


_INIT_ERROR_MSG = "Trait sanity test: Nature instance hasn't been properly set "
    "on initialization. Either you are using Trait outside of Nature scope or "
    "Nature initialization hasn't been finished yet."
_LABEL_ERROR_MSG = "Trait sanity test: trait label hasn't been properly set on "
    "initialization. Either you are using Trait outside of Nature scope or "
    "Nature initialization hasn't been finished yet."


class Trait(object):

    # pattern for __dict__ key on the Nature; space char is intended to be
    # sure we are not colliding with any proper attribute name
    _listener_key_pattern = '%s change listeners'

    def __init__(self, default=None, validators=None, volatile=False):
        """
        Params:
            default - default value of the Trait. It is not validated, so you
                are supposed to know what you are doing. None is treated as no
                default value. Default: None
            validators - iterable of (value) -> None functions that are called
                when Trait changes its value. They are supposed to raise
                TraitValidationError if they consider value to be invalid.
                Validators are supported on per-Nature-class basis.
            volatile - trait should not be treated as persistent. Default: False.
        """
        # the Nature instance and the label (name of the trait on the Nature)
        # are to be injected from the Nature scope
        self._instance = None
        self._label = None
        # kwargs
        self.default = default
        self.validators = validators or ()

    @property
    def instance(self):
        """
        Instance of Nature that owns this trait. The value of self._instance is
        injected during Nature metaclass execution.
        """
        assert self._instance, _INIT_ERROR_MSG
        return self._instance

    @property
    def label(self):
        """
        Python name of the attribute under which the trait is hung on
        the Nature that owns this trait. The value of self._label is
        injected during Nature metaclass execution.
        """
        assert isinstance(self._label, six.string_types), _LABEL_ERROR_MSG
        return self._label

    def _get_value(self):
        """
        Technical method for retrieving the value from the instance `__dict__`.
        """
        return self._instance.__dict__.get(self._label, self.default)

    def _set_value(self, value):
        """
        Technical method for setting the value from the instance `__dict__`.
        """
        return self._instance.__dict__[self._label] = value

    @property
    def _value_types(self):
        """
        Overridden in descendants to define basic types of valid values.
        """
        raise TraitInstantiationError("You shouldn't use pure Trait class.")

    # Descriptor protocol

    def __get__(self, instance, owner):
        """
        If accessed from the instance, gets the value of the trait from the
        Nature `__dict__`.
        If accessed from the class, lets interact with the trait itself.
        """
        assert instance is self._instance or instance is None, _INIT_ERROR_MSG
        assert isinstance(self._label, six.string_types), _LABEL_ERROR_MSG
        # Nature class case; let interact with the trait itself
        if instance is None:
            return self
        # Nature instance case; interact with the value of the trait
        return self._get_value()

    def __set__(self, instance, new_value):
        """
        Iff value has changed, __set__ validates the value, updates itself and
        notifies all change listeners.
        """
        assert instance and instance is self._instance, _INIT_ERROR_MSG
        assert isinstance(self._label, six.string_types), _LABEL_ERROR_MSG
        value_changed = (new_value != self._get_value())
        if value_changed:
            # logic fires only in the case when the value changes
            self.validate(new_value)
            self._set_value(new_value)
            # notify observers about change done
            key = self._listener_key_pattern % self._label
            for listener in instance.__class__.__dict__.get(key, ()):
                listener(self.__value, new_value, instance)

    def __delete__(self, obj):
        # TODO Deletes the record (as usual) or sets the value to undefined/None?
        del self.instance.__dict__[self._label]
        # or self._set_value(undefined)

    # Validation

    def validate(self, value):
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
        if not isinstance(value, self._value_types):
            msg = "Invalid type of value: was {}; should be: {}".format(
                type(value), self._value_types)
            raise TraitValidationError(msg)
        for validator in self.validators:
            validator(value)

    # Observable pattern

    def change_listener(self, listener):
        """
        Decorator that marks a function or method as a change listener on
        per-Nature-class basis.

        Params:
            listener - a function or method of
                    (old_value, new_value, Trait) -> None
                signature that is going to be called whenever the trait changes
                its value. It is supposed to serve as a listener of the trait
                value. The listeners are supported on per-Nature-class basis.
        Returns:
            the initial `listener` argument
        """
        assert self._instance, _INIT_ERROR_MSG
        assert isinstance(self._label, six.string_types), _LABEL_ERROR_MSG
        key = self._listener_key_pattern % self._label
        # per-class change listeners

        # TODO should I hang per-Nature-class attributes on Nature class or
        # on trait instance? if on trait, Nature-implementing class must be
        # hashable
        nature = self._instance.__class__
        if key not in nature.__dict__:
            nature.__dict__[key] = set()
        nature.__dict__[key].add(listener)
        # it's intended as a decorator, so return the `listener`
        return listener
