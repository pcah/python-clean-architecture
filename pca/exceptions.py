# -*- coding: utf-8 -*-


class DharmaError(Exception):
    """Base error class for all errors from Dharma module"""

    DEFAULT_AREA = None
    DEFAULT_CODE = None
    PRINTED_ATTRS = (
        'area',
        'code'
    )

    def __init__(self, code=None, area=None):
        self.area = area or self.DEFAULT_AREA
        self.code = code or self.DEFAULT_CODE
        super(DharmaError, self).__init__()

    def __str__(self):
        return "{}({})".format(self._get_class_name(), ", ".join(
            "{}='{}'".format(attr, getattr(self, attr) or 'None')
            for attr in self.PRINTED_ATTRS
        ))

    __repr__ = __str__

    def _get_class_name(self):
        return self.__class__.__name__


class DharmaConfigError(DharmaError):
    """An error was encountered during configuration of Dharma"""
    DEFAULT_AREA = 'CONF'


class TraitError(DharmaError):

    PRINTED_ATTRS = DharmaError.PRINTED_ATTRS + ('trait',)

    """Base error class for all Trait-related errors"""
    def __init__(self, trait=None, *args, **kwargs):
        super(TraitError, self).__init__(*args, **kwargs)
        self.trait = trait


class TraitInstantiationError(TraitError):
    """Error class for errors related to the instantiation of a trait"""
    # TODO is it still needed?
    # TOMBSTONE 19.09.2016 or upon traits package finished milestone


class TraitValidationError(TraitError):
    """
    Error class raised by trait validators during pca.data.Trait.validate.

    It can be also used to summarize multiple single validation errors using
    errors argument.
    """
    DEFAULT_AREA = 'VALID'
    PRINTED_ATTRS = TraitError.PRINTED_ATTRS + ('errors',)

    def __init__(self, errors=None, *args, **kwargs):
        super(TraitValidationError, self).__init__(*args, **kwargs)
        self.errors = errors


class TraitPreprocessorError(TraitValidationError):
    """
    Error class raised during pca.data.Trait._preprocess_value as a wrapper
    to any error that might happen during preprocessing. Concrete error is
    stored under __context__ attribute (as in python 3.x during reraising).

    This error class inherrits from TraitValidationError, so that one have
    a unified way of gathernig errors during trait assignment.
    """
    DEFAULT_CODE = 'PREPROCESSOR-ERROR'

    def __init__(self, context, *args, **kwargs):
        super(TraitPreprocessorError, self).__init__(
            errors={'_preprocess_value': context}, *args, **kwargs)
        self.__context__ = context


class TraitRequiredError(TraitValidationError):
    """
    Error class describing unfulfilled required attribute. This means that
    during Nature's validation process the trait.is_empty == True while
    trait.required == True.
    """
    DEFAULT_CODE = 'TRAIT-REQUIRED'


class PathNotFoundError(DharmaError):
    DEFAULT_AREA = 'INT'
    DEFAULT_CODE = 'PREDICATE-PATH-NOT-FOUND'
    PRINTED_ATTRS = DharmaError.PRINTED_ATTRS + ('args',)


class RepoError(DharmaError):
    """
    Base class for errors concerning repositories and DB handling.
    """
    DEFAULT_AREA = 'REPO'


class RepoUpdateNotUniqueError(RepoError):
    """
    Error class thrown iff content of the update to a repo is not unique, ie.
    it contains duplicate entries to a single entity.
    """
    DEFAULT_CODE = 'REPO-UPDATE-NOT-UNIQUE'

    def __init__(self, common, *args, **kwargs):
        super(RepoUpdateNotUniqueError, self).__init__(*args, **kwargs)
        self.common = common
