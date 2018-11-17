# -*- coding: utf-8 -*-
from jsonweb import decode, encode
import six

from pca.utils.inspect import get_func_name


def policy_constructor(cls, d):
    """
    Pass all the kwargs but __type__ (which was already used to choose `cls`
    class) to the class __init__.
    """
    d.pop('__type__')
    instance = cls(**d)
    return instance


class PolicyMeta(type):
    """
    A metaclass that is enwrapping the class with JsonWeb encode/decode
    decorators.
    """

    def __new__(mcs, name, bases, attrs):
        """Enwrap the class with JsonWeb decorators"""
        cls = type.__new__(mcs, name, bases, attrs)
        cls = encode.to_object()(cls)
        cls = decode.from_object(policy_constructor)(cls)
        return cls


@six.add_metaclass(PolicyMeta)
class Policy(object):
    """
    A self-JSON-serializable class which consists of:
    * a collection of persistent attributes, defined by SERIALIZED_ATTRS list,
    * a collections of functions [sic!], defined by STRATEGY_CHOICES dict.

    Attributes which names are listed in SERIALIZED_ATTRS (and only those) are
    serialized.

    STRATEGY_MODULE defines a module which declares some collections of
    functions. Keys of STRATEGY_CHOICES dict are names of strategy_roles,
    which serves as names of groups of strategies and kwargs of
    Policy.__init__. Values of STRATEGY_CHOICES are lists of names of
    functions from STRATEGY_MODULE. They describe valid choices of values to
    appropriate Policy.__init__ kwargs.

    If you search for an example, look at the tests at tests/domain/policy.py

    NB: Comparing equality of two policies focus only on comparing values of
    SERIALIZED_ATTRS and STRATEGY_CHOICES.keys()
    """

    # module from which strategies are imported
    STRATEGY_MODULE = object()
    # dict of role_name: a list of strategy_names
    STRATEGY_CHOICES = {}
    # a list of attributes to be persisted by to_json handler
    SERIALIZED_ATTRS = ()

    def __init__(self, **strategies):
        """
        Params:
            strategies - a dictionary of strategy_role: strategy_name
                where strategy_role is a key to STRATEGY_CHOICES dict, and
                strategy_name is pythonic name of the strategy function.
        """
        assert set(strategies.keys()) == set(self.STRATEGY_CHOICES.keys()), (
            "Invalid set of strategies. Given: {}. Expected: {}.".format(
                strategies.keys(), self.STRATEGY_CHOICES.keys()))

        # get strategy functions for all roles declared by STRATEGY_CHOICES
        # for each role
        for role in strategies:
            # take declared strategy name
            assert strategies[role] in self.STRATEGY_CHOICES[role], (
                "Unknown strategy name '{}' for the role '{}'".format(
                    strategies[role], role))
            # look for such name in the module
            strategy = getattr(self.STRATEGY_MODULE, strategies[role], None)
            if strategy is None:
                raise ValueError((
                    "Strategy named '{}' for the role of '{}' not found in the"
                    " '{}' module.").format(
                        strategies[role], role, self.STRATEGY_MODULE))
            # and set it on self under the role name
            setattr(self, role, strategy)

    @encode.handler
    def to_json(self):
        """
        'Manual' serializer method which encodes strategy method *names*
        (normally, functions aren't serializable).
        """
        # names of all strategy functions under strategy role keys
        d = dict(
            (role, get_func_name(getattr(self, role)))
            for role in self.STRATEGY_CHOICES
        )
        # additional attributes to serialize
        d.update(
            (key, getattr(self, key))
            for key in self.SERIALIZED_ATTRS
        )
        # __type__ name for jsonweb object_hook
        d['__type__'] = type(self).__name__
        return d

    def __eq__(self, other):
        """
        Equality compares only serializable SERIALIZED_ATTRS and strategies
        declared in STRATEGY_CHOICES.
        """
        attrs = set(self.SERIALIZED_ATTRS).union(other.SERIALIZED_ATTRS)
        strategy_roles = set(self.STRATEGY_CHOICES).union(
            other.STRATEGY_CHOICES)

        def compare_attrs(attrs):
            return all(
                getattr(self, attr) == getattr(other, attr) for attr in attrs)

        return compare_attrs(attrs) and compare_attrs(strategy_roles)
