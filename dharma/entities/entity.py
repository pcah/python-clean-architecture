import six

from ..traits import Trait


class Options(object):
    """
    That's a counterpart of the wrapper of class named Meta of Django Model.
    """

    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.kwargs = kwargs

    def traits(self):
        " Returns traits of the owning Entity "
        raise NotImplementedError  # TODO


class EntityMeta(type):
    " The metaclass doing hard job building API of Entity "

    def __new__(cls, name, bases, attrs):
        # supply all traits with their labels
        attrs_orig = attrs.copy()  # shallow copy for iterating on unchanged iterable
        for name, attr in attrs_orig.items():
            # instantiate uninstantiated Traits (feature # TODO)
            if issubclass(attr, Trait):
                attrs[name] = attr = attr()
            # inform the trait instance about its name on the entity
            if isinstance(attr, Trait):
                attr.label = name
        # build the entity and its meta options
        opts_dict = attrs.pop('EntityOpts', {})  # XXX error, a class instance cant be unsplat later!
        self = super(EntityMeta, cls).__new__(cls, name, bases, attrs)
        self.entity_opts = Options(self, **opts_dict)
        return self


class Entity(six.with_metaclass(EntityMeta, object)):
    pass
