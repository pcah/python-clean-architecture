import six

from ..exceptions import TraitInstantiationError
from ..utils import is_argspec_valid, OrderedSet


_INIT_ERROR_MSG = (
    "Trait sanity test: Nature instance hasn't been properly set"
    " on initialization. Either you are using Trait outside of Nature scope or"
    " Nature initialization hasn't been finished yet.")
_LABEL_ERROR_MSG = (
    "Trait sanity test: trait label hasn't been properly set on"
    " initialization. Either you are using Trait outside of Nature scope or "
    "Nature initialization hasn't been finished yet.")
_INVALID_SIGN_MSG = (
    "Trait sanity test: function passed to the listener seems to have invalid "
    "signature. Check method docstring for details.")
_INVALID_SIGN_MSG = (
    "Trait sanity test: function passed to the listener seems not to have valid"
    " signature. Check method docstring for details.")
_CAST_TYPE_ERROR = (
    "Trait sanity test: you're trying to use a casting trait without correctly "
    "specifying the casting type.")



class Trait(object):
    """
    Nature
    observable
    validation
    default value
    """

    # pattern for __dict__ key on the Nature; space char is intended to be
    # sure we are not colliding with any proper attribute name
    _listener_key_pattern = '%s change listeners'

    _cast_to = None

    def __init__(self, default=None, cast=False, validators=None,
                 class_listeners=None, volatile=False):
        """
        Params:
            default - default value of the Trait. It is not validated (you
                are supposed to know what you are doing). None is treated as no
                default value. Default: None
            validators - iterable of (value, Nature) -> None functions that
                are called when Trait changes its value. They are supposed
                to raise `TraitValidationError` if they consider value to be
                invalid. Nature argument is given for the sake of cross-trait
                validation on Nature instance. Validators are supported
                on per-Nature-class basis.
            cast - a boolean describing whether value assigned to the trait
                should be casted to the expected type of value. Casting is done
                before validation. Default: False
            class_listeners - iterable of per-Nature-class listeners. Trait
                implements observable pattern, including on Trait instance per
                the Nature-implementing class. With this argument you can
                declare the listeners during Trait declaration.
            volatile - trait should not be treated as persistent.
                Default: False.
        """
        # the Nature instance and the label (name of the trait on the Nature)
        # are to be injected from the Nature scope
        self._instance = None
        self._label = None

        # kwargs
        self.default = default
        self.validators = validators or ()
        self.cast = cast
        self._cast_to = None
        # ordered set of change listeners per-Nature-class
        self._class_listeners = OrderedSet(listeners) if listeners else None

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
        self._instance.__dict__[self._label] = value

    @property
    def _value_types(self):
        """
        Overridden in descendants to define basic types of valid values.
        """
        raise TraitInstantiationError("You shouldn't use pure Trait class.")

    ############
    # Descriptor protocol
    ############

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

        old_value = self._get_value()
        new_value = self._preprocess_value(new_value)
        if new_value != old_value:
            # logic fires only in the case when the value changes
            if self.cast:
                new_value = self.cast(new_value)
            else:
                self.validate_type(new_value)
            self.validate_value(new_value)
            # the new value is assumed to be valid
            self._set_value(new_value)
            # notify listeners about change done
            self._notify(old_value)

    def __delete__(self, obj):
        # TODO Deletes the record (as usual) or sets the value to undefined/None?
        del self.instance.__dict__[self._label]
        # or self._set_value(undefined)

    ############
    # Validation
    ############

    def _preprocess_value(self, value):
        """
        A hook for preparing assigned value BEFORE value is checked whether it
        is to be changed. Useful if your assigning process has to change
        the value in some way, ie. instantiates the class of the value.

        Params:
            value - raw value to reprocess.
        Returns:
            Preprocessed value.
        """
        return value

    def cast(self, value):
        """
        Casts new value to the type specified by `_cast_to` attribute.
        Can be used as a hook for more sophisticated logic.

        Param:
            value - value to be cast.

        Returns:
            casted value.
        """
        assert self._cast_to, _CAST_TYPE_ERROR
        return self._cast_to(value)

    def validate_type(self, value):
        if not isinstance(value, self._value_types):
            msg = "Invalid type of value: was {}; should be: {}".format(
                type(value), self._value_types)
            raise TraitValidationError(msg)

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

    ############
    # Observable pattern for Nature class & instance
    ############

    def _notify(self, old_value):
        """
        Fires notifications to per-class and per-instance listeners. Old value
        is passed as argument, new value is just the current value (we are at
        the point right after the assignment).

        Params:
            old_value - trait value before assignment.

        Returns:
            None.
        """
        new_value = self._get_value()
        instance = self._instance
        # per-Nature-class listeners
        if self._class_listeners:
            for listener in self._class_listeners:
                # TODO do we need to pass the instance?
                listener(old_value, new_value, instance)
        # per-Nature-instance listeners
        key = self._listener_key_pattern % self._label
        if key in instance.__dict__:
            for listener in instance.__dict__.get(key, ()):
                # TODO do we need to pass the instance?
                listener(old_value, new_value, instance)

    def add_class_listener(self, listener):
        """
        Adds a function or method as a change listener on
        per-Nature-class basis.

        Params:
            listener - a function or method of
                    (old_value, new_value, Trait) -> None
                signature that is going to be called whenever the trait changes
                its value. It is supposed to serve as a listener of the trait
                value. The listeners are supported on per-Nature-class basis.
        Returns:
            None
        """
        if not self._class_listeners:
            self._class_listeners = OrderedSet()
        self._class_listeners.append(listener)

    def class_listener(self, listener):
        """
        Decorator that marks a function or method as a change listener on
        per-Nature-class basis. To be used within the Nature scope.

        Params:
            listener - a function or method of
                    (old_value, new_value, Trait) -> None
                signature that is going to be called whenever the trait changes
                its value. It is supposed to serve as a listener of the trait
                value. The listeners are supported on per-Nature-class basis.
        Returns:
            the initial `listener` argument untouched. It just adds it to the
            internal collection of listeners of the Trait.
        """
        self.add_class_listener(listener)
        # it's intended as a decorator, so return the `listener` untouched
        return listener

    def add_instance_listener(self, listener):
        """
        Adds a function or method as a change listener on
        per-Nature-instance basis.

        Params:
            listener - a function or method of
                    (old_value, new_value, Trait) -> None
                signature that is going to be called whenever the trait changes
                its value. It is supposed to serve as a listener of the trait
                value. The listeners are supported on per-Nature-instance
                basis.
        Returns:
            None
        """
        assert self._instance, _INIT_ERROR_MSG
        assert isinstance(self._label, six.string_types), _LABEL_ERROR_MSG
        # we're asserting valid listener signature (without relying on
        # duck-typing), because listener is passed here, but the potential
        # TypeError is going to be raised much further during the runtime
        assert is_argspec_valid(listener, arg_number=3), _INVALID_SIGN_MSG

        # per-Nature-instance change listeners
        # trait signs itself with its label in the instance __dict__
        key = self._listener_key_pattern % self._label
        nature = self._instance
        if key not in nature.__dict__:
            nature.__dict__[key] = OrderedSet()
        nature.__dict__[key].add(listener)

