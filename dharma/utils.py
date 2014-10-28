from collections import namedtuple
import copy


class frozendict(dict):
    """
    Frozen (unmutable) version of dict. Name is left to be consistent with
    set/frozenset pair.

    The code is taken from:
    code.activestate.com/recipes/414283-frozen-dictionaries/
    """

    @property
    def _blocked_attribute(obj):
        raise AttributeError("A frozendict cannot be modified.")

    __delitem__ = __setitem__ = clear = _blocked_attribute
    pop = popitem = setdefault = update = _blocked_attribute

    def __new__(cls, *args, **kw):
        new = dict.__new__(cls)

        args_ = []
        for arg in args:
            if isinstance(arg, dict):
                arg = copy.copy(arg)
                for k, v in arg.items():
                    if isinstance(v, dict):
                        arg[k] = frozendict(v)
                    elif isinstance(v, list):
                        v_ = list()
                        for elm in v:
                            if isinstance(elm, dict):
                                v_.append(frozendict(elm))
                            else:
                                v_.append(elm)
                        arg[k] = tuple(v_)
                args_.append( arg )
            else:
                args_.append( arg )

        dict.__init__(new, *args_, **kw)
        return new

    def __init__(self, *args, **kw):
        pass

    def __hash__(self):
        try:
            return self._cached_hash
        except AttributeError:
            h = self._cached_hash = hash(frozenset(self.items()))
            return h

    def __repr__(self):
        return "frozendict(%s)" % dict.__repr__(self)


class OrderedSet(set):
    pass  # TODO


def is_argspec_valid(function, arg_number=None, kwargs_names=None):
    """
    Args:
        function - function to be checked.
        arg_number - number of all arguments (named or not) which is going to
            be used calling the function.
        kwargs_names - iterable of names for keyword arguments whose existence
            in signature is going to be verified.

    Returns:
        bool - True iff function is valid to be valid with specified arg
            number and keyword arguments names.
    """
    # TODO if six.PY3 use SignatureObject
    # else:
    # import inspect
    # (len(inspect.getargspec(listener).args) == 3 or
    #  inspect.getargspec(listener).varargs is not None)
    return True


# Named tuple of (trait_class, args=(), kwargs={}) schema
TraitDefinition = namedtuple('TraitDefinition', ['trait_class', 'args', 'kwargs'])
TraitDefinition.__new__.__defaults__ = ((), frozendict())
