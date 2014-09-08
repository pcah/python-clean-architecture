from collections import namedtuple


class frozendict(dict):
    """
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


# Named tuple of (trait_class, args=(), kwargs={}) schema
TraitDefinition = namedtuple('TraitDefinition', ['trait_class', 'args', 'kwargs'])
TraitDefinition.__new__.__defaults__ = ((), frozendict())
