"""
Sentinel class for immutables with useful reprs.
"""
from collections import namedtuple
from operator import itemgetter

Sentinel = namedtuple("Sentinel", ["module", "name"])
# shadowing attributes as unmodifiable
Sentinel.module = property(itemgetter(0))
Sentinel.name = property(itemgetter(1))
