import typing as t

from pca.utils.collections import OrderedSet
from pca.utils.inspect import is_argspec_valid
from pca.utils.sentinel import Sentinel


# sentinel object for expressing that a value of a observable hasn't been set
# NB: None object might be a valid value
undefined_value = Sentinel(module='pca.data.observable', name='undefined_value')


Owner = t.TypeVar('Owner')
Value = t.TypeVar('Value')
Preprocessor = t.Callable[[Value], Value]
Validator = t.Callable[[Value], None]  # raises errors
Observer = t.Callable[[Owner, Value, Value], None]


class Observable:

    _owner: Owner
    _label: str
    # pattern for __dict__ key on the owner class; space char is intended to be
    # sure we are not colliding with any proper attribute name
    _observer_key_pattern = '%s instance observers'

    def __init__(
            self,
            default=undefined_value,
            preprocessor: Preprocessor = None,
            validator: Validator = None,
            class_observers: t.Iterable[Observer] = None
    ):
        """
        Params:
            default -- default value of the Observable. It is not validated (you are supposed to
                know what you are doing).
                Default: sentinel object "pca.data.observable.undefined_value"
            preprocessor -- a callable of signature:
                    (raw_value) -> value
                which prepares what's going-to-be new value before the assignment and the validity
                checks. It's usable when you want to cast the value, instantiate a class to be
                a value or something similar.
            validator -- a callable of signature:
                    (old_value) -> None
                which checks if the value is valid, whatever that means to the observable.
            class_observers -- iterable of per-class observers. With this argument you can declare
                the observers during Observable declaration.
        """
        self.default = default
        self.preprocessor = preprocessor
        self.validator = validator
        self._class_observers = OrderedSet(class_observers) if class_observers else OrderedSet()

    def __set_name__(self, owner, name):
        self._owner = owner
        self._label = name

    @property
    def label(self) -> str:
        """Python name of the attribute under which the observable is hung on the owner class."""
        return self._label

    def _get_value(self, instance: Owner) -> Value:
        """Technical detail of retrieving the value from the instance `__dict__`."""
        return instance.__dict__.get(self._label, self.default)

    def _set_value(self, instance: Owner, value: Value):
        """Technical detail of setting the value at the instance `__dict__`."""
        instance.__dict__[self._label] = value

    def __get__(self, instance: Owner, owner: t.Type) -> Value:
        """
        If accessed from the instance, gets the value of the observable from
        the owner's `__dict__`.
        If accessed from the class, lets interact with the observable itself.
        """
        if instance is None:
            return self
        return self._get_value(instance)

    def __set__(self, instance: Owner, new_value: Value) -> None:
        """
        Iff value has changed, __set__ processes the value, validates it, updates itself and
        notifies all change observers.
        """
        old_value = self._get_value(instance)
        new_value = self._preprocess(new_value)
        if new_value is not old_value:
            # logic fires only in the case when the value changes
            self._validate(instance, new_value)
            # the new value is assumed to be valid
            self._set_value(instance, new_value)
            # notify observers about the change done
            self._notify(instance, old_value, new_value)

    def __delete__(self, instance: Owner) -> None:
        """
        Sets default (undefined_value by default) as the value of the observable.

        NB: if the observable hasn't been set at all, there's no value, there is only
        a `self.default` attribute.
        """
        self._set_value(instance, self.default)

    def _preprocess(self, value: Value) -> Value:
        """
        Prepares assigned value BEFORE value is checked whether it is to be changed. Useful if
        your assigning process has to change the value in some way, ie. instantiates the class
        of the value or casts the value.

        Params:
            value -- raw value to reprocess.
        Returns:
            Preprocessed value.
        """
        if not self.preprocessor:
            return value
        return self.preprocessor(value)

    def _validate(self, instance: Owner, new_value: Value = None) -> None:
        """
        Fires validator using instance, old_value and new_value as arguments.

        The `validate` method may be called with a to-be-assigned value as the `new_value`
        in purpose of validating it pre-assignment;  or without a new_value which means that
        the current value is validated.

        Params:
            instance -- instance of the owner
            new_value -- a value which is supposed to be set on the observable; the default value
                is the current value of the observable
        Raises:
            errors that are used by the validator
        """
        if not self.validator:
            return
        old_value = self._get_value(instance)
        new_value = new_value or old_value
        self.validator(instance, old_value, new_value)

    def _notify(self, instance: Owner, old_value: Value, new_value: Value) -> None:
        """
        Fires notifications to per-class and per-instance observers. Old value is passed
        as an argument, new value is just the current value (we are at the point right after
        the assignment).

        Params:
            instance -- instance of the owner.
            old_value -- value before assignment.
            new_value -- current value of the observable.
        """
        # per-instance observers
        key = self._observer_key_pattern % self._label
        for observer in instance.__dict__.get(key, ()):
            observer(instance, old_value, new_value)

        # per-class observers
        for observer in self._class_observers or ():
            observer(instance, old_value, new_value)

    def add_class_observer(self, observer: Observer) -> None:
        """
        Adds a function or method as a change observer on per-class basis.

        Params:
            observer -- a function or method of
                    (Observable, old_value, new_value) -> None
                signature that is going to be called whenever the observable changes its value.
                It is supposed to serve as a observer of the observable's value.
        """
        # TODO assert observer signature is valid
        self._class_observers.add(observer)

    def class_observer(self, observer: Observer) -> Observer:
        """
        Decorator that marks a function or method as a change observer on per-class basis.

        Params:
            observer -- a function or method of
                    (observable, old_value, new_value) -> None
                signature that is going to be called whenever the observable changes its value.
                It is supposed to serve as a observer of the observable's value.
        Returns:
            the initial `observer` argument untouched. It just adds it to the internal collection
            of observers of the Observable.

        Example usage:

            class MyObject:
                some_observable = Observable()

                @some_observable.class_observer
                def some_observable_activated(self, old_value, new_value, observable):
                    do_sth_here
        """
        # TODO assert observer signature is valid
        self.add_class_observer(observer)
        # it's intended as a decorator, so return the `observer` untouched
        return observer

    def add_instance_observer(self, instance: Owner, observer: Observer) -> None:
        """
        Adds a function or method as a change observer on per-instance basis.

        Params:
            instance - the owner instance that the observer is connected to
            observer - a function or method of
                    (owner_instance, old_value, new_value) -> None
                signature that is going to be called whenever the observable changes its value.
                It is supposed to serve as a observer of the observable's value.
        """
        # we're asserting valid observer signature (without relying on
        # duck-typing), because observer is passed here, but the potential
        # TypeError is going to be raised much further during the runtime
        # TODO assert observer signature is valid
        assert is_argspec_valid(observer, arg_number=3)

        # per-instance change observers
        # observable signs itself with its label in the instance __dict__
        key = self._observer_key_pattern % self._label
        instance.__dict__.setdefault(key, OrderedSet()).add(observer)
