from abc import (
    ABC,
    abstractmethod,
)
from functools import reduce
from operator import and_
import typing as t

from pca.interfaces.dao import (
    Id,
    Ids,
    IDao,
    IQueryChain,
    Row,
    Rows,
)

from .formulae import Predicate


class QueryChain(IQueryChain):
    """
    Technical detail of chaining queries.

    A proxy for a query interface of DAO, gathering lazy evaluated queries
    (ie. filter, sort, aggregate, etc) to call owning DAO to resolve them when non-lazy
    (ie. get, exists, count, update, etc) is called.
    """

    # TODO lazy queries: filter(id=...), sort, aggregate, annotate
    # TODO evaluating queries: slicing

    def __init__(self, dao: 'AbstractDao', _filters: t.List[Predicate] = None):
        super().__init__(dao, _filters)
        self._dao = dao
        self._filters = _filters or []

    @property
    def _is_trivial(self) -> bool:
        """Trivial QueryChain is the one that has no lazy operations defined."""
        return not self._filters

    @property
    def _reduced_filter(self) -> t.Optional[Predicate]:
        """Before evaluation, sum up all filter predicates into a single one"""
        if self._is_trivial:
            return
        return reduce(and_, self._filters)

    # lazy queries

    def filter(self, predicate: Predicate) -> 'QueryChain':
        """
        Creates a new QueryChain with the list of filter predicates extended.
        """
        return self.__class__(self._dao, self._filters + [predicate])

    # evaluating queries

    def __iter__(self) -> Row:
        """Yields values"""
        yield from self._dao._resolve_filter(self._reduced_filter)

    def __len__(self) -> int:
        """Proxy for `count`."""
        return self.count()

    def get(self, id_: Id) -> Row:
        """
        Returns row of given id.

        :raises: NotFound iff row of given id is not present.
        """
        return self._dao._resolve_get(self, id_)

    def get_or_none(self, id_: Id) -> t.Optional[Row]:
        """Returns row of given id, or None iff not present."""
        return self._dao._resolve_get(self, id_, nullable=True)

    def exists(self) -> bool:
        """Returns whether any row specified by the query exist."""
        return self._dao._resolve_exists(self)

    def count(self) -> int:
        """
        Counts rows filtering them out by the query specifying conditions that they
        should met.
        """
        return self._dao._resolve_count(self)

    # evaluating commands

    def update(self, update: Row) -> Ids:
        """
        Updates all rows specified by the query with given update.
        """
        return self._dao._resolve_update(self, update)

    def remove(self) -> Ids:
        """
        Removes all rows specified by the query from the collection.
        """
        return self._dao._resolve_remove(self)


class AbstractDao(IDao[Id], ABC):
    """Base abstract implementation for Data Access Object."""

    # lazy queries

    def all(self) -> QueryChain:
        """
        Returns a query chain representing all rows.

        Useful to explicitly denote counting, updating or removing all rows.
        """
        return QueryChain(self)

    def filter(self, predicate: Predicate) -> QueryChain:
        """
        Filters out rows by the predicate specifying conditions that they
        should met. Can be chained via `QueryChain` helper class.
        """
        return QueryChain(self, [predicate])

    # evaluating queries

    def get(self, id_: Id) -> Row:
        """
        Returns row of given id.
        Shortcut for querying via `QueryChain.all`.

        :raises: NotFound iff row of given id is not present.
        """
        return self._resolve_get(None, id_)

    def get_or_none(self, id_: Id) -> t.Optional[Row]:
        """
        Returns row of given id, or None iff not present.
        Shortcut for querying via `QueryChain.all`.
        """
        return self._resolve_get(None, id_, nullable=True)

    @abstractmethod
    def _resolve_filter(self, predicate: Predicate) -> Rows:
        """Resolves filtering for any other resolving operation to compute."""

    @abstractmethod
    def _resolve_get(
            self, query_chain: t.Optional[QueryChain], id_: Id, nullable: bool = False
            ) -> Row:
        """
        Returns row of given id or raises a NotFound error.
        """

    @abstractmethod
    def _resolve_exists(self, predicate: QueryChain) -> bool:
        """Returns whether any row specified by the query exist."""

    @abstractmethod
    def _resolve_count(self, query_chain: QueryChain) -> int:
        """
        Counts rows filtering them out by the query specifying conditions that they should met.
        """

    # evaluating commands

    @abstractmethod
    def _resolve_update(self, query_chain: QueryChain, update: Row) -> Ids:
        """
        Updates all rows specified by the query with given update.
        """

    @abstractmethod
    def _resolve_remove(self, query_chain: QueryChain) -> Ids:
        """
        Removes all rows specified by the query from the collection.
        """

    # instant commands

    @abstractmethod
    def insert(self, row: Row) -> Id:
        """
        Inserts the row into the collection.

        :returns: id of the inserted row
        """

    @abstractmethod
    def batch_insert(self, rows: Rows) -> Ids:
        """
        Inserts multiple rows into the collection.

        :returns: a iterable of ids
        """

    @abstractmethod
    def clear(self) -> None:
        """Clears the collection."""
