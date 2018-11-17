"""
Sentinel class for immutables with useful reprs.
"""
from __future__ import absolute_import
from collections import namedtuple
from operator import itemgetter

Sentinel = namedtuple("Sentinel", ["module", "name"])
# shadowing attributes as unmodifiable
Sentinel.module = property(itemgetter(0))
Sentinel.name = property(itemgetter(1))
