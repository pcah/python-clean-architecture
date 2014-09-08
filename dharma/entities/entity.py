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
        raise NotImplementedError


class EntityMeta(type):
    " The metaclass doing hard job building API of Entity "

    def __new__(cls, name, bases, attrs):
        # supply all traits with their labels
        for name, attr in attrs.items():
            if isinstance(attr, Trait):
                attr.label = name
        # build the meta options
        opts_dict = attrs.pop('_Opts', {})
        self = super(EntityMeta, cls).__new__(cls, name, bases, attrs)
        attrs['_opts'] = Options(self, **opts_dict)
        return self


class Entity(six.with_metaclass(EntityMeta, object)):
    pass
