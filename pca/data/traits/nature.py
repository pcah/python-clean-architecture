"""
Module 'pca.traits.nature' defines minimal API for a trait-oriented class.
Look at docstrings of Nature, NatureMeta and Dharma classes.
"""
# pylint: disable=protected-access, too-few-public-methods

import six

from pca.exceptions import TraitRequiredError, TraitValidationError
from pca.utils import frozendict, get_func_name
from .trait import Trait


class Dharma(object):
    """
    A class gathering meta-control and meta-info features of a
    Nature-implementing class. This is a counterpart of the wrapper class named
    Meta of Django Model/ModelForm.
    """

    def __init__(self, nature, traits, dharma=None):
        """
        Params:
            nature - Nature class owning this Dharma instance
            traits - iterable of all traits of the nature
            dharma - "meta"-class interpreted as a definition for the Dharma.
                    It is supposed to have attributes that Dharma interprets as
                    its parameters:
                cross_validators - a dictionary of signature
                        validation_function: list_of_trait_names
                    consisting of cross-validation functions which arguments
                    are consistent with the list of trait names given as dict
                    values.
        """
        self.nature = nature
        self._traits = frozendict(traits)
        self._required = frozendict(
            (label, trait) for label, trait in traits.items()
            if trait.required
        )
        self.cross_validators = {}
        if dharma:
            # process the definition of the dharma
            if hasattr(dharma, 'cross_validators'):
                for validator, trait_names in dharma.cross_validators.items():
                    assert set(self._traits) <= trait_names, (
                        "Dharma cross-validator '{}' has been described to "
                        "use trait name(s) that are not defined on the Nature"
                        "; Nature traits: {}; validator arguments: {}"
                    ).format(validator, self._traits, trait_names)
                self.cross_validators = dharma.cross_validators

    @property
    def traits(self):
        """Lists all traits of the nature"""
        return self._traits

    @property
    def required(self):
        """Lists required traits of the nature"""
        return self._required

    def validate(self, instance):
        """
        Check for non-empty values at required traits, validates each one of
        them if
        and fires cross-trait validation.

        Params:
            instance -- the Nature instance.

        Raises:
            TraitValidationError which summarizes validation problems.
        """
        errors = {}

        for trait_name, trait in self._traits.items():
            # required check
            if trait.required and trait.is_empty(instance):
                errors[trait_name] = TraitRequiredError(trait=trait)
                continue
            # fire Trait.validate
            try:
                trait.validate(instance)
            except TraitValidationError as e:
                errors[trait_name] = e.errors if e.errors else e
        # cross-validation
        for validator, trait_names in self.cross_validators.items():
            trait_values = dict(
                (name, getattr(instance, name)) for name in trait_names
            )
            try:
                validator(**trait_values)
            except Exception as e:
                name = get_func_name(validator)
                assert name not in errors
                errors[name] = e
        # and finally raise summary of errors
        if errors:
            raise TraitValidationError(errors=errors)

    def __getitem__(self, item):
        """Returns the trait of specified name"""
        return self._traits[item]


class NatureMeta(type):
    """
    The metaclass that is doing the hard job building API of Nature.
    """

    def __new__(mcs, name, bases, attrs):
        # fetch Dharma definition
        dharma = attrs.pop('Dharma', None)
        assert not isinstance(dharma, Trait) and attrs.get('dharma') is None, (
            "Trait sanity test -- you probably didn't want to pass a Trait as "
            "a Dharma")
        # create the type instance
        cls = super(NatureMeta, mcs).__new__(mcs, name, bases, attrs)
        traits = {}
        for name, attr in attrs.items():
            if isinstance(attr, Trait):
                # gathering traits and their labels for Dharma
                traits[name] = attr
                # injecting label & instance to the traits
                attr._label = name
                attr._nature = cls
        cls.dharma = Dharma(nature=cls, traits=traits, dharma=dharma)
        return cls


class Nature(six.with_metaclass(NatureMeta, object)):
    """
    A trait-oriented mixin. Subclassing the Nature makes:
    * your Trait attributes enabled,
    * an automatically added 'dharma' attribute, which serves all
        trait-oriented meta-level control and information for your
        Nature-implementing class.
    """
    dharma = None

    def __new__(cls):
        instance = super(Nature, cls).__new__(cls)
        # inject instance to the trait
        for trait in cls.dharma.traits.values():
            trait._instance = instance
        # TODO copy class' Dharma object as an instance Dharma with injected
        # instance
        return instance

    # TODO __init__ kwargs to initialize traits
