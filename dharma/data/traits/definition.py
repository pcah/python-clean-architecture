from collections import namedtuple

from dharma.utils import frozendict


# Named tuple of (trait_class, args=(), kwargs={}) schema
TraitDefinition = namedtuple(
    'TraitDefinition', ['trait_class', 'args', 'kwargs']
)
TraitDefinition.__new__.__defaults__ = ((), frozendict())
