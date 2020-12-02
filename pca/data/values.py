import typing as t

from pca.utils.sentinel import Sentinel


undefined_value = Sentinel(module="pca.data.descriptors", name="undefined_value")

Owner = t.TypeVar("Owner")
Value = t.TypeVar("Value")
