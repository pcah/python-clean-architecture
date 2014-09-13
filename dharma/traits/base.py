import six

from ..exceptions import TraitInstantiationError


INIT_ERROR_MSG = "Trait sanity test: Nature instance hasn't been properly set "
    "on initialization."
LABEL_ERROR_MSG = "Trait sanity test: trait label hasn't been properly set on "
    "initialization."


class Trait(object):

    # pattern for __dict__ key on the Nature; space char is intended as not to collide with any proper attribute name
    __callbacks_key_pattern = '%s callbacks'

    def __init__(self, default=None, validators=None, callbacks=None,
                 volatile=False):
        """
        Params:
            default - default value of the Trait. It is not validated, so you
                are supposed to know what you are doing. None is treated as no
                default value. Default: None
            validators - iterable of (value) -> None functions that are called
                when Trait changes its value. They are supposed to raise
                TraitValidationError if they consider value to be invalid.
                Validators are supported on per-class manner.
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
        assert self._instance, INIT_ERROR_MSG
        return self._instance

    @property
    def label(self):
        """
        Python name of the attribute under which the trait is hung on
        the Nature that owns this trait. The value of self._label is
        injected during Nature metaclass execution.
        """
        assert self._label, LABEL_ERROR_MSG
        return self._label

    def _check_nature(self):
        """
        Checks whether _label and _instance were correctly injected. It would
        be the other way iff someone assigned Trait to a class that doesn't
        implement the Nature mixin.
        """
        # TODO remove asserts from the methods? or leave to have the asserts transparent in -O(ptimalization) mode of Python
        assert instance and instance is self._instance, INIT_ERROR_MSG
        assert isinstance(self._label, six.binary_type), LABEL_ERROR_MSG

    def _get_value(self):
        " Technical method for retrieving the value from the instance __dict__ "
        return self._instance.__dict__.get(self._label, self.default)

    def _set_value(self, value):
        " Technical method for setting the value from the instance __dict__ "
        return self._instance.__dict__[self._label] = value

    @property
    def _value_types(self):
        " Overridden in descendants to define basic types of valid values. "
        raise TraitInstantiationError("You shouldn't use pure Trait class.")


    # Descriptor protocol

    def __get__(self, instance, owner):
        " Gets the value from the Nature "
        assert instance is self._instance or instance is None, INIT_ERROR_MSG
        assert isinstance(self._label, six.binary_type), LABEL_ERROR_MSG
        # class case: the trait is called from the Nature class
        if instance is None:
            return self
        # instance case
        return self._get_value()

    def __set__(self, instance, new_value):
        assert instance and instance is self._instance, INIT_ERROR_MSG
        assert isinstance(self._label, six.binary_type), LABEL_ERROR_MSG
        value_changed = (new_value != self._get_value)
        if value_changed:
            # TODO validate on every assign or only on value_changed?
            self.validate(new_value)
            # notify observers
            callbacks_key = self.__callbacks_key_pattern % self._label
            for callback in instance.__dict__.get(callbacks_key, ()):
                callback(self.__value, new_value, instance)
            self._set_value(new_value)

    def __delete__(self, obj):
        # TODO Deletes the record (as usual) or sets the value to undefined/None?
        del self.instance.__dict__[self._label]
        # or self._set_value(undefined)

    def validate(self, value):
        if not isinstance(value, self._value_types):
            msg = "Invalid type of value: was {}; should be of {}".format(
                type(value), self._value_types)
            raise TraitValidationError(msg)
        for validator in self.validators:
            validator(value)

    def add_callback(self, callback):
        """
        Add a new function to call every time the descriptor within instance
        updates.

        Params:
            instance - Nature instance that contains the
            callback - (old_value, new_value, Trait) -> None
                function that is called when trait changes its value. It is
                supposed to serve as observer of the trait value. The callbacks
                are supported on per-instance manner.
        """
        assert instance and instance is self._instance, INIT_ERROR_MSG
        assert isinstance(self._label, six.binary_type), LABEL_ERROR_MSG
        key = self.__callbacks_key_pattern % self._label
        instance = self._instance
        if key not in instance.__dict__:
            instance.__dict__[key] = set()
        instance.__dict__[key].add(callback)
