import typing as t

from pca.exceptions import RepoError

Id = t.TypeVar('Id', int, str, t.Tuple)
Ids = t.Iterable[Id]
Row = t.Mapping[str, t.Any]
Rows = t.TypeVar('Rows', t.Iterable[Row], t.Sized)


class IPredicate:
    """Interface of logical predicate."""


class IQueryChain(t.Iterable[Row], t.Sized, t.Generic[Id]):
    """
    Technical detail of chaining queries.

    A proxy for a query interface of DAO, gathering lazy evaluated queries
    (ie. filter, sort, aggregate, etc) to call owning DAO to resolve them when non-lazy
    (ie. get, exists, count, update, etc) is called.
    """

    # TODO lazy queries: sort, aggregate, annotate
    # TODO evaluating queries: slicing

    def __init__(self, dao: 'IDao', _filters: t.List[IPredicate] = None):
        ...

    # lazy queries

    def filter(self, predicate: IPredicate) -> 'IQueryChain':
        """
        Filters out rows by the predicate specifying conditions that they
        should met. Can be chained via `IQueryChain` helper class.
        """

    # evaluating queries

    def __iter__(self) -> Row:
        """Yields values"""

    def get(self, id_: Id) -> Row:
        """
        Returns row of given id.

        :raises: NotFound iff row of given id is not present.
        """

    def get_or_none(self, id_: Id) -> t.Optional[Row]:
        """Returns row of given id, or None iff not present."""

    def exists(self) -> bool:
        """Returns whether any row specified by the query exist."""

    def __len__(self) -> int:
        """Same as `count`."""

    def count(self) -> int:
        """
        Counts rows filtering them out by the query specifying conditions that they
        should met.
        """

    # evaluating commands

    def update(self, update: Row) -> Ids:
        """
        Updates all rows specified by the query with given update.
        """

    def remove(self) -> Ids:
        """
        Removes all rows specified by the query from the collection.
        """


class IDao(t.Generic[Id]):
    """
    Interface for Data Access Object. Describes an abstraction over any kind
    of collections of rows of data: both relational database's tables and
    non-relational document sets, etc.
    """

    class NotFound(RepoError):
        PRINTED_ATTRS = RepoError.PRINTED_ATTRS + ('id_',)
        DEFAULT_CODE = 'NOT-FOUND'

        def __init__(self, *args, id_, **kwargs):
            super().__init__(*args, **kwargs)
            self.id_ = id_

    # lazy queries

    def all(self) -> IQueryChain:
        """
        Returns a query chain representing all rows.

        Useful to explicitly denote counting, updating or removing all rows.
        """

    def filter(self, predicate: IPredicate) -> IQueryChain:
        """
        Filters out rows by the predicate specifying conditions that they
        should met. Can be chained via `IQueryChain` helper class.
        """

    # evaluating queries

    def get(self, id_: Id) -> Row:
        """
        Returns row of given id.
        Shortcut for querying via `IDao.all`.

        :raises: NotFound iff row of given id is not present.
        """

    def get_or_none(self, id_: Id) -> t.Optional[Row]:
        """
        Returns row of given id, or None iff not present.
        Shortcut for querying via `IDao.all`.
        """

    # instant commands

    def insert(self, row: Row) -> Id:
        """
        Inserts the row into the collection.

        :returns: id of the inserted row
        """

    def batch_insert(self, rows: Rows) -> Ids:
        """
        Inserts multiple rows into the collection.

        :returns: a iterable of ids
        """

    def clear(self) -> None:
        """
        Removes all items from the collection.
        """
