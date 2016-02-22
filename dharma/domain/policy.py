from jsonweb import decode, encode
import six

from dharma.utils.inspect import get_func_name


def policy_constructor(cls, d):
    """
    Pass all the kwargs but __type__ (which was already used to choose `cls`
    class) to the class __init__.
    """
    d.pop('__type__')
    instance = cls(**d)
    return instance


@encode.to_object()
@decode.from_object(policy_constructor)
class PolicyMeta(type):

    def __new__(mcs, name, bases, attrs):
        cls = type.__new__(mcs, name, bases, attrs)
        return cls


@six.add_metaclass(PolicyMeta)
class Policy(object):

    # module from which strategies are imported
    STRATEGY_MODULE = None
    # dict of role_name: a list of strategy_names
    STRATEGY_CHOICES = {'generate_food': 1}
    # a list of attributes to be persisted by to_json handler
    SERIALIZED_ATTRS = ('turn_length',)

    BOARD_CLASS = None

    def __init__(self, turn_length, **strategies):
        """
        Params:
            turn_length - turn time length in miliseconds; this is how long
                server will wait for the players to give orders.
            strategies - a dictionary of strategy_role: strategy_name
                where strategy_role is a key to STRATEGY_CHOICES dict, and
                strategy_name is pythonic name of the strategy function.
        """
        assert self.BOARD_CLASS, "No BOARD_CLASS declared."
        assert set(strategies.keys()) == set(self.STRATEGY_CHOICES.keys()), (
            "Invalid set of strategies. Given: {}. Expected: {}.".format(
                strategies.keys(), self.STRATEGY_CHOICES.keys()))

        self.turn_length = turn_length

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
        d.update(dict(
            (key, getattr(self, key))
            for key in self.SERIALIZED_ATTRS
        ))
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
