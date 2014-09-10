import six

from ..exceptions import TraitInstantiationError


class Trait(object):

    # pattern for __dict__ key on the entity; space char is intended as not to collide with any proper attribute name
    __callbacks_key_pattern = '%s callbacks'

    def __init__(self, default=None, validators=None):
        # the entity instance and the label (name of the trait on the entity) are to be injected from the entity scope
        self.instance = None
        self.label = None
        # kwargs
        self.default = default
        self.validators = validators or ()

    def _get_value(self):
        " Technical method for retrieving the value from the instance __dict__ "
        return self.instance.__dict__.get(self.label, self.default)

    def _set_value(self, value):
        " Technical method for setting the value from the instance __dict__ "
        return self.instance.__dict__[self.label] = value

    @property
    def _value_types(self):
        " Overridden in descendants to define basic types of valid values. "
        raise TraitInstantiationError("You shouldn't use pure Trait class.")


    # Descriptor protocol

    def __get__(self, instance, owner):
        " Gets the value from the entity "
        assert instance is self.instance or instance is None, "Trait sanity test: owning entity hasn't been properly set on initialization."
        assert isinstance(self.label, six.binary_type), "Trait sanity test: trait label hasn't been properly set."
        # class case: the trait is called from the Entity class
        if instance is None:
            return self
        # instance case
        return self._get_value()

    def __set__(self, instance, new_value):
        assert instance and instance is self.instance, "Trait sanity test: owning entity hasn't been properly set on initialization."
        assert isinstance(self.label, six.binary_type), "Trait sanity test: trait label hasn't been properly set."
        value_changed = (new_value != self._get_value)
        self.validate(new_value)  # TODO validate on every assign or only on value_changed?
        if value_changed:
            # notify observers
            callbacks_key = self.__callbacks_key_pattern % self.label
            for callback in instance.__dict__.get(callbacks_key, ()):
                callback(self.__value, new_value, instance)
            self._set_value(new_value)

    def __delete__(self, obj):
        # TODO Deletes the record (as usual) or sets the value to undefined/None?
        del self.instance.__dict__[self.label]
        # or self._set_value(undefined)

    def validate(self, value):
        if not isinstance(value, self._value_types):
            msg = "Invalid type of value: was {}; should be of {}".format(
                type(value), self._value_types)
            raise TraitValidationError(msg)
        for validator in self.validators:
            validator(value)

    def add_callback(self, instance, callback):
        """Add a new function to call every time the descriptor within instance updates"""
        key = self.__callbacks_key_pattern % self.label
        if key not in instance.__dict__:
            instance.__dict__[key] = set()
        instance.__dict__[key].add(callback)
