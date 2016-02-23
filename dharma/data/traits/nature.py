"""
Module 'dharma.traits.nature' defines minimal API for a trait-oriented class.
Look at docstrings of Nature, NatureMeta and Dharma classes.
"""
# pylint: disable=protected-access, too-few-public-methods

import six

from dharma.utils import frozendict
from .base import Trait


class Dharma(object):
    """
    A class gathering meta-control and meta-info features of a
    Nature-implementing class. This is a counterpart of the wrapper class named
    Meta of Django Model/ModelForm.
    """

    def __init__(self, nature, traits, dharma=None, **kwargs):
        """
        Params:
            nature - Nature instance owning this Dharma instance
            traits - iterable of all traits of the nature
            dharma - "meta"-class interpreted as a definition for the Dharma.
                It is supposed to have attributes that Dharma interprets as
                its parameters.
        """
        self._nature = nature
        self._kwargs = kwargs
        self._traits = frozendict(traits)
        if dharma:
            # process the definition of the dharma
            pass  # TODO

    @property
    def traits(self):
        " Returns traits of the Nature "
        return self._traits


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
        cls.dharma = Dharma(nature=cls, dharma=dharma, traits=traits)
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
        return instance
