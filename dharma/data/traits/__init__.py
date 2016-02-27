from .base import Trait  # noqa
from .nature import Nature  # noqa
from .simple_traits import Int, Long, Float, Complex, Text
# from .collection import Mapping, Sequence
# from .type_based import Instance, Type


Mapping = Sequence = Instance = Type = lambda x: x

SIMPLE_TRAITS = [Int, Text, Long, Float, Complex]
ENUMERATE_TRAITS = []
COLLECTION_TRAITS = [Mapping, Sequence]
TYPE_BASED_TRAITS = [Instance, Type]
