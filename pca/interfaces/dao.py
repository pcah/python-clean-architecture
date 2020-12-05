import typing as t

from .entity import (
    Id,
    Ids,
)


Kwargs = t.Dict[str, t.Any]
BatchOfKwargs = t.Sequence[Kwargs]


class Dto(Kwargs, dict):
    """
    Represents a Data Transfer Object retrieved from some Data Access Object.

    DTO is a `dict`-like object with some identity (a property) set by the persistence layer
    lying beneath the DAO. DTOs carry de-structured and normalized data of some kind of domain
    entity, intended to be put into the persistence layer.
    """

    __id__: Id = None

    @property
    def id(self) -> Id:
        """
        Defines access to the primary key of the DTO.

        NB: simple case of DAOs will use an `int` as an Id, while more complex cases may use
        a non-standard data type or a composite of some values (as a tuple).
        """
        return self.__id__


BatchOfDto = t.TypeVar("BatchOfDto", t.Iterable[Dto], t.Sized)


class IPredicate:
    """Interface of logical predicate."""


class IQueryChain(t.Iterable[Dto], t.Sized, t.Generic[Id]):
    """
    Technical detail of chaining queries.

    A proxy for a query interface of DAO, gathering lazy evaluated queries
    (ie. filter, sort, aggregate, etc) to call owning DAO to resolve them when non-lazy
    (ie. get, exists, count, update, etc) is called.
    """

    # TODO lazy queries: order_by, aggregate, annotate
    # TODO evaluating queries: slicing

    # lazy queries

    def filter(self, predicate: IPredicate) -> "IQueryChain":
        """
        Filters out objects by the predicate specifying conditions that they
        should met. Can be chained via `IQueryChain` helper class.
        """
        raise NotImplementedError

    def filter_by(self, id_: Id = None, ids: Ids = None) -> "IQueryChain":
        """
        Filters objects by a single id or a iterable of ids.

        :raises: InvalidQueryError if:
            * both `id_` and `ids` arguments are defined
            * or the query is already filtered by id
        """
        raise NotImplementedError

    # evaluating queries

    def __iter__(self) -> Dto:
        """Yields values"""
        raise NotImplementedError

    def get(self, id_: Id) -> t.Optional[Dto]:
        """Returns object of given id, or None iff not present."""
        raise NotImplementedError

    def exists(self) -> bool:
        """Returns whether any object specified by the query exist."""
        raise NotImplementedError

    def __len__(self) -> int:
        """Same as `count`."""
        raise NotImplementedError

    def count(self) -> int:
        """
        Counts objects filtering them out by the query specifying conditions that they
        should met.
        """
        raise NotImplementedError

    # evaluating commands

    def update(self, **update) -> Ids:
        """
        Updates all objects specified by the query with given update.
        """
        raise NotImplementedError

    def remove(self) -> Ids:
        """
        Removes all objects specified by the query from the collection.
        """
        raise NotImplementedError


class IDao(t.Generic[Id]):
    """
    Interface for Data Access Object. Describes an abstraction over any kind
    of collections of objects of data: both relational database's tables and
    non-relational document sets, etc.
    """

    # lazy queries

    def all(self) -> IQueryChain:
        """
        Returns a query chain representing all objects.

        Useful to explicitly denote counting, updating or removing all objects.
        """
        raise NotImplementedError

    def filter(self, predicate: IPredicate) -> IQueryChain:
        """
        Filters out objects by the predicate specifying conditions that they
        should met.
        Can be chained with other queries via `IQueryChain` helper.
        """
        raise NotImplementedError

    def filter_by(self, id_: Id = None, ids: Ids = None) -> IQueryChain:
        """
        Filters objects by a single id or a iterable of ids.
        Can be chained with other queries via `IQueryChain` helper.

        :raises: InvalidQueryError if:
            * both `id_` and `ids` arguments are defined
            * or the query is already filtered by id
        """
        raise NotImplementedError

    # evaluating queries

    def get(self, id_: Id) -> t.Optional[Dto]:
        """
        Returns object of given id, or None iff not present.
        Shortcut for querying via `IDao.all`.
        """
        raise NotImplementedError

    # instant commands

    def insert(self, **kwargs) -> Id:
        """
        Inserts the object into the collection.

        :returns: id of the inserted object
        """
        raise NotImplementedError

    def batch_insert(self, batch_kwargs: BatchOfKwargs) -> Ids:
        """
        Inserts multiple objects into the collection.

        :returns: a iterable of ids
        """
        raise NotImplementedError

    def clear(self) -> None:
        """
        Removes all items from the collection.
        """
        raise NotImplementedError
