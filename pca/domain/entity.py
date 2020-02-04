import abc
import dataclasses
import typing as t
from uuid import UUID, uuid4

# from pca.utils.collections import frozen  # TODO
from pca.utils.compat import GenericABCMeta

# TODO #40. is entity module using dataclasses `field` or have its own API for `fields`?
# proxy import for now
field = dataclasses.field


IdType = t.TypeVar('IdType')


class Id(t.Generic[IdType], metaclass=GenericABCMeta):
    """
    Abstract base class for descriptors of identity. The most common usage is
    describing identity of Entity subclasses.
    """

    _ID_ATTR_NAME: t.ClassVar[str] = '__id__'

    def __set_name__(self, owner: t.Any, name: str) -> None:
        self.owner = owner
        self.name = name

    def __get__(self, instance, owner) -> t.Union['Id', t.Tuple]:
        if not instance:
            return self
        return getattr(instance, self._ID_ATTR_NAME, None)

    @classmethod
    @abc.abstractmethod
    def __set_id__(cls, instance: t.Any, id_value: IdType = None) -> t.Any:
        """Implements technical details of setting an ID value to the field."""


class AutoId(Id[IdType]):
    """
    Descriptor describing identity of an entity as auto-generated value.
    Strategy of value generation is set as an `generator` argument.
    """
    def __init__(self, generator: t.Callable[[], IdType]) -> None:
        """
        A function, passed as `generator` argument, will be used to generate
        identity key.
        """
        self._generator = generator

    def __set_id__(self, instance: t.Any, id_value: IdType = None) -> None:
        """Generates a new ID always when its value has not been passed."""
        id_value = self._generator() if id_value is None else id_value
        setattr(instance, self._ID_ATTR_NAME, id_value)


class SequenceId(AutoId[int]):
    """
    Naive identity descriptor that keeps count of sequent generations. The counter
    is per-descriptor-instance, so an inherited field on multiple subclasses
    has the same counter.

    NB: Doesn't take into account either collisions in the effect of any concurrency
    nor any kind of synchronization between instances of ID field.
    """
    def __init__(self):
        from itertools import count
        self._counter = count(1)
        super().__init__(generator=lambda: next(self._counter))


class Uuid4Id(AutoId[UUID]):
    """
    Identity descriptor that auto-generates UUID v4, which are random
    Universally Unique Identifiers of 128-bit length.
    """
    def __init__(self):
        super().__init__(generator=uuid4)


class NaturalId(Id):
    """
    Descriptor describing identity of an entity as a tuple of its unique and
    immutable values forming a natural ID.
    """
    def __init__(self, *field_names: str):
        """
        Given field_names are fields of the owner to build an identity key.
        """
        assert field_names
        self._field_names = field_names

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        annotations = {
            name: owner.__annotations__.get(name, None)
            for name in self._field_names
        }
        assert all(annotations.values()), (
            f"Entity owner has to have all field_names as dataclass "
            f"annotations: {self._field_names}"
        )
        # TODO assert immutability of the fields

    def __set_id__(self, instance: t.Any, id_value: IdType = None) -> None:
        own_id_value = tuple(getattr(instance, v) for v in self._field_names)
        setattr(instance, self._ID_ATTR_NAME, own_id_value)


@dataclasses.dataclass(eq=False)
class Entity(t.Generic[IdType]):
    """
    Entity is a business logic pattern: it is thought to have a set of fields and methods
    that embody some knowledge about the domain.
    * Entity class is structured, which means that some relation to other entity is represented by
      concrete reference to the other object.
    * Entity (and an aggregate root especially) should represent complex data and shouldn't
      be normalized.
    """
    __id_field_name__: t.ClassVar[str]

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        id_fields = [(k, v) for k, v in cls.__dict__.items() if isinstance(v, Id)]
        if not getattr(cls, '__id_field_name__', None):
            assert len(id_fields) == 1, (
                f"Exactly one ID field is required for any Entity class. Got: "
                f"{dict(id_fields) if id_fields else None}"
            )
            cls.__id_field_name__ = id_fields[0][0]
        return dataclasses.dataclass(cls, eq=False)

    def __init__(self, **kwargs):
        """
        This initializer will be overridden by dataclass decorator above. It is needed to
        persuade static type checkers that Entities have initializers.
        """

    @classmethod
    def __get_id_field__(cls) -> Id:
        """Returns the field assumed to be the identity descriptor."""
        return getattr(cls, cls.__id_field_name__)

    def __get_id__(self) -> IdType:
        """Returns value of the identity field."""
        return getattr(self, self.__id_field_name__)

    def __set_id__(self, id_value: IdType = None) -> 'Entity':
        self.__get_id_field__().__set_id__(self, id_value)
        return self

    def __eq__(self, other) -> bool:
        """Entity is identified by the value of its `Id` field."""
        return isinstance(other, self.__class__) and other.__get_id__() == self.__get_id__()
