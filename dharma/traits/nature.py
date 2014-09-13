import six

from dharma.utils import frozendict
from .base import Trait


class Dharma(object):
    """
    A class gathering meta-control and meta-info features of a
    Nature-implementing class. This is a counterpart of the wrapper class named
    Meta of Django Model/ModelForm.
    """

    def __init__(self, nature, traits, dharma_def=None):
        """
        Params:
            nature - Nature instance owning this Dharma instance
            traits - iterable of all traits of the nature
            dharma_def - "meta"-class interpreted as a definition for
                the Dharma. It is supposed to have attributes that
                Dharma interprets as its parameters.
        """
        self._nature = nature
        self._kwargs = kwargs
        self._traits = frozendict(traits)
        if dharma_def:
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

    def __new__(cls, name, bases, attrs):
        # supply all traits with their labels
        traits = {}
        # shallow copy for iterating on unchanged iterable, because attrs dict
        # will be changed
        for name, attr in attrs.copy():
            # instantiate uninstantiated Traits (feature # TODO)
            if issubclass(attr, Trait):
                attrs[name] = attr = attr()
            # inform the trait instance about its name on the Nature
            if isinstance(attr, Trait):
                # injecting label & instance to the traits
                attr._label = name
                attr._instance = self
                # gathering traits and their labels for Dharma
                traits[name] = attr
        # build the Nature and its meta options
        dharma_def = attrs.pop('Dharma', None)
        assert not isinstance(dharma, Trait), "Trait sanity test: you probably"
            "didn't want to pass a Trait as a Dharma"
        self = super(NatureMeta, cls).__new__(cls, name, bases, attrs)
        self.dharma = Dharma(nature=self, dharma_def=dharma_def, traits=traits)
        return self


class Nature(six.with_metaclass(NatureMeta, object)):
    """
    A trait-oriented mixin. Subclassing the Nature makes:
    * your Trait attributes enabled,
    * an automatically added 'dharma' attribute, which serves all
        trait-oriented meta-level control and information for your
        Nature-implementing class.
    """
