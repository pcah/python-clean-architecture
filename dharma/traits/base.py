from weakref import WeakKeyDictionary

from ..exceptions import TraitInstantiationError


class Trait(object):
    def __init__(self, default=None):
        self.label = None  # name of the trait on the entity; to be injected from the entity scope
        self.default = default
        self.callbacks = WeakKeyDictionary()

    def __get__(self, instance, owner):
        " Gets the value from the entity __dict__"
        # class case: the trait is called from the Entity class
        if instance is None:
            return self
        # instance case
        if not self.label:
            raise TraitInstantiationError
        return instance.__dict__.get(self.label, self.default)

    def __set__(self, instance, value):
        if not self.label:
            raise TraitInstantiationError
        value_changed = value != instance.__dict__.get(self.label, self.default)
        if value_changed:
            self._validate(value)
            # notify observers
            for callback in self.callbacks.get(instance, []):
                callback(old_value, new_value, instance)
            # store the value on the instance
            instance.__dict__[self.label] = value

    def __delete__(self, obj):
        " Deletes the record (as usual) or sets the value to undefined/None "
        raise NotImplementedError

    def _validate(self, value):
        if not isinstance(value, self._value_types):
            raise TraitValidationError()  # TODO

    @property
    def _value_types(self):
        " Overridden in descendants to define basic types of valid values. "
        raise TraitInstantiationError("You shouldn't use pure Trait class.")

    def add_callback(self, instance, callback):
        """Add a new function to call every time the descriptor within instance updates"""
        if instance not in self.callbacks:
            self.callbacks[instance] = []
        self.callbacks[instance].append(callback)
