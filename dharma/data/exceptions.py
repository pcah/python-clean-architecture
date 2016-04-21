# -*- coding: utf-8 -*-


class TraitError(Exception):
    def __init__(self, trait=None, *args, **kwargs):
        super(TraitError, self).__init__(*args, **kwargs)
        self.trait = trait

    def __str__(self):
        return "{result}; trait: {trait}".format(
            result=super(TraitError, self).__repr__(),
            trait=self.trait or 'None')


class TraitInstantiationError(TraitError):
    pass


class TraitValidationError(TraitError):
    """
    Error class raised by trait validators during dharma.data.Trait.validate.

    It can be also used to summarize multiple single validation errors using
    errors argument.
    """
    def __init__(self, errors=None, *args, **kwargs):
        super(TraitValidationError, self).__init__(*args, **kwargs)
        self.errors = errors

    def __str__(self):
        return "{result}; errors: {errors}".format(
            result=super(TraitValidationError, self).__repr__(),
            errors=self.errors or 'None')


class TraitPreprocessorError(TraitValidationError):
    """
    Error class raised during dharma.data.Trait._preprocess_value as a wrapper
    to any error that might happen during preprocessing. Concrete error is
    stored under __context__ attribute (as in python 3.x during reraising).

    This error class inherrits from TraitValidationError, so that one have
    a unified way of gathernig errors during trait assignment.
    """
    def __init__(self, context, *args, **kwargs):
        super(TraitPreprocessorError, self).__init__(
            errors={'_preprocess_value': context}, *args, **kwargs)
        self.__context__ = context
