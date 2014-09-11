import six

from .base import Trait


class Dharma(object):
    """
    That's a counterpart of the wrapper of class named Meta of Django Model.
    """

    def __init__(self, nature, **kwargs):
        self.nature = nature
        self.kwargs = kwargs

    def traits(self):
        " Returns traits of the owning Nature "
        raise NotImplementedError  # TODO


class NatureMeta(type):
    " The metaclass doing hard job building API of Nature "

    def __new__(cls, name, bases, attrs):
        # supply all traits with their labels
        attrs_orig = attrs.copy()  # shallow copy for iterating on unchanged iterable
        for name, attr in attrs_orig.items():
            # instantiate uninstantiated Traits (feature # TODO)
            if issubclass(attr, Trait):
                attrs[name] = attr = attr()
            # inform the trait instance about its name on the Nature
            if isinstance(attr, Trait):
                attr.label = name
        # build the Nature and its meta options
        dharma = attrs.pop('Dharma', None)
        assert not isinstance(dharma, Trait), "Trait sanity test: you probably didn't want to pass a Trait as a Dharma"
        self = super(NatureMeta, cls).__new__(cls, name, bases, attrs)
        self.dharma = Dharma(self, dharma)
        return self


class Nature(six.with_metaclass(NatureMeta, object)):
    pass