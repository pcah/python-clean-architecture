# -*- coding: utf-8 -*-
import six

from dharma.data.exceptions import (  # noqa
    TraitInstantiationError,
    TraitValidationError,
)
from dharma.utils import get_func_name, is_argspec_valid, OrderedSet, Sentinel
from .validation import construct_validators


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

# sentinel object for expressing that a value of a trait hasn't been set
# NB: None object might be a valid value set on a trait
undefined_value = Sentinel('undefined_value', 'dharma.data.traits')


class Trait(object):
    """
    Nature
    observable
    """

    # pattern for __dict__ key on the Nature; space char is intended to be
    # sure we are not colliding with any proper attribute name
    _listener_key_pattern = '%s instance listeners'

    def __init__(self, genus=None, default=undefined_value, validators=None,
                 class_listeners=None):
        """
        Params:
            genus -- type of the trait, that is used by validation mechanism;
                it might be expressed with:
                * a simple class (int, dict, str, etc.),
                * a class from the 'typing' module (vide: PEP 0484),
                * a class from .typing (This, etc.)
                * a string with a name from the above cases.
            default -- default value of the Trait. It is not validated (you
                are supposed to know what you are doing).
                Default: sentinel object "dharma.data.traits.undefined_value"
            class_listeners -- iterable of per-Nature-class listeners. Trait
                implements observable pattern, including on Trait instance per
                the Nature-implementing class. With this argument you can
                declare the listeners during Trait declaration.
        """
        # the label (name of the trait on the Nature) is to be injected from
        # the Nature scope
        self._label = None
        # validation
        self.genus = genus
        self.validators = construct_validators(genus) if genus else \
            OrderedSet()
        if validators:
            self.validators.update(validators)
        self.default = default
        # ordered set of change listeners per-Nature-class
        self._class_listeners = OrderedSet(class_listeners) \
            if class_listeners else OrderedSet()

    @property
    def label(self):
        """
        Python name of the attribute under which the trait is hung on
        the Nature that owns this trait. The value of self._label is
        injected during Nature metaclass execution.
        """
        return self._label

    def _get_value(self, instance):
        """
        Technical method for retrieving the value from the instance `__dict__`.
        """
        return instance.__dict__.get(self._label, self.default)

    def _set_value(self, instance, value):
        """
        Technical method for setting the value from the instance `__dict__`.
        """
        instance.__dict__[self._label] = value

    ############
    # Descriptor protocol
    ############

    def __get__(self, instance, owner):
        """
        If accessed from the instance, gets the value of the trait from the
        Nature `__dict__`.
        If accessed from the class, lets interact with the trait itself.
        """
        assert isinstance(self._label, six.string_types), _LABEL_ERROR_MSG
        # Nature class case; let interact with the trait itself
        if instance is None:
            return self
        # Nature instance case; interact with the value of the trait
        return self._get_value(instance)

    def __set__(self, instance, new_value):
        """
        Iff value has changed, __set__ validates the value, updates itself and
        notifies all change listeners.
        """
        assert instance  # TODO error message
        assert isinstance(self._label, six.string_types), _LABEL_ERROR_MSG

        old_value = self._get_value(instance)
        new_value = self.preprocess_value(new_value)
        if new_value != old_value:
            # logic fires only in the case when the value changes
            self.validate(instance, new_value)
            # the new value is assumed to be valid
            self._set_value(instance, new_value)
            # notify listeners about the change done
            self._notify(instance, old_value)

    def __delete__(self, instance):
        self._set_value(instance, undefined_value)

    ############
    # Validation
    ############

    def preprocess_value(self, value):
        """
        A hook for preparing assigned value BEFORE value is checked whether it
        is to be changed. Useful if your assigning process has to change
        the value in some way, ie. instantiates the class of the value or
        casts the value.

        Params:
            value -- raw value to reprocess.
        Returns:
            Preprocessed value.
        """
        return value

    def validate(self, instance, new_value):
        """
        Fires all validators using new_value as an argument
        Params:
            instance -- instance of the Nature
            new_value -- a value which is supposed to be set on the trait
        Raises:
            TraitValidationError -- error with dictionary of errors from
                validators.
        """
        errors = {}
        for validator in self.validators:
            try:
                validator(instance, new_value)
            except Exception as e:
                errors[get_func_name(validator)] = e
        if errors:
            raise TraitValidationError(errors=errors, trait=self)

    ############
    # Observable pattern for Nature class & instance
    ############

    def _notify(self, instance, old_value):
        """
        Fires notifications to per-class and per-instance listeners. Old value
        is passed as argument, new value is just the current value (we are at
        the point right after the assignment).

        Params:
            old_value -- trait value before assignment.

        Returns:
            None.
        """
        new_value = self._get_value(instance)
        # per-Nature-class listeners
        if self._class_listeners:
            for listener in self._class_listeners:
                listener(instance, old_value, new_value)
        # per-Nature-instance listeners
        key = self._listener_key_pattern % self._label
        if key in instance.__dict__:
            for listener in instance.__dict__.get(key, ()):
                listener(instance, old_value, new_value)

    def add_class_listener(self, listener):
        """
        Adds a function or method as a change listener on
        per-Nature-class basis.

        Params:
            listener -- a function or method of
                    (Trait, old_value, new_value) -> None
                signature that is going to be called whenever the trait changes
                its value. It is supposed to serve as a listener of the trait
                value. The listeners are supported on per-Nature-class basis.
        Returns:
            None
        """
        # TODO assert listener signature is valid
        self._class_listeners.add(listener)

    def class_listener(self, listener):
        """
        Decorator that marks a function or method as a change listener on
        per-Nature-class basis. To be used within the Nature scope.

        Params:
            listener -- a function or method of
                    (old_value, new_value, Trait) -> None
                signature that is going to be called whenever the trait changes
                its value. It is supposed to serve as a listener of the trait
                value. The listeners are supported on per-Nature-class basis.
        Returns:
            the initial `listener` argument untouched. It just adds it to the
            internal collection of listeners of the Trait.

        Example usage:

            class MyObject(Nature):
                some_trait = Int

                @some_trait.class_listener
                def some_trait_activated(self, old_value, new_value, trait):
                    do_sth_here
        """
        self.add_class_listener(listener)
        # it's intended as a decorator, so return the `listener` untouched
        return listener

    def add_instance_listener(self, instance, listener):
        """
        Adds a function or method as a change listener on
        per-Nature-instance basis.

        Params:
            instance - the Nature instance that the listener is connected to
            listener - a function or method of
                    (old_value, new_value, Trait) -> None
                signature that is going to be called whenever the trait changes
                its value. It is supposed to serve as a listener of the trait
                value. The listeners are supported on per-Nature-instance
                basis.
        Returns:
            None
        """
        assert isinstance(self._label, six.string_types), _LABEL_ERROR_MSG
        # we're asserting valid listener signature (without relying on
        # duck-typing), because listener is passed here, but the potential
        # TypeError is going to be raised much further during the runtime
        assert is_argspec_valid(listener, arg_number=3), _INVALID_SIGN_MSG

        # per-Nature-instance change listeners
        # trait signs itself with its label in the instance __dict__
        key = self._listener_key_pattern % self._label
        if key not in instance.__dict__:
            instance.__dict__[key] = OrderedSet()
        instance.__dict__[key].add(listener)
