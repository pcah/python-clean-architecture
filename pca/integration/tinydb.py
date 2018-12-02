# -*- coding: utf-8 -*-
import typing as t

from pca.exceptions import (
    ConfigError,
    DependencyNotFoundError,
    InvalidQueryError,
)
from pca.data.dao import (
    AbstractDao,
    Id,
    Ids,
    Predicate,
    QueryChain,
    Row,
    Rows,
)
from pca.utils.dependency_injection import Container

try:
    import tinydb
except ImportError:  # pragma: no cover
    tinydb = None


class TinyDbDao(AbstractDao[int]):
    """
    Adapts `tinydb.Table` to IDao interface.

    Caches instances representing different files, because TinyDb is not
    """
    _db_cache: t.ClassVar[t.Dict[str, 'tinydb.TinyDB']] = {}

    @classmethod
    def clear_db_cache(cls):
        cls._db_cache.clear()

    def __init__(self, container: Container, **kwargs):
        if not tinydb:  # pragma: no cover
            raise DependencyNotFoundError('tinydb')

        self._container = container
        self._path = kwargs.get('path')
        """
        Path is needed to be specified when TinyDb gets JSONStorage (default one).
        We use value of path for identifying different DBs of TinyDb.
        If the path is not specified, we can assume that the intention is to use
        MemoryStorage (if not explicitly defined) and not to cache the TinyDb instance.
        """

        self._table_name = kwargs.pop('table_name', None) or kwargs.pop('qualifier', None)
        if not self._table_name:
            raise ConfigError(code='NO-TABLE-NAME-PROVIDED')

        if self._path:
            if self._path not in self._db_cache:
                self._db_cache[self._path] = tinydb.TinyDB(**kwargs)
            self._db: tinydb.TinyDB = self._db_cache[self._path]
        else:
            if 'storage' not in kwargs:
                kwargs['storage'] = tinydb.storages.MemoryStorage
            self._db = tinydb.TinyDB(**kwargs)
        self._table: tinydb.database.Table = self._db.table(self._table_name)

    def _resolve_filter(self, predicate: t.Optional[Predicate]) -> Rows:
        """Resolves filtering for any other resolving operation to compute."""
        if not predicate:
            return self._table.all()
        return self._table.search(predicate)

    def _resolve_get(
            self, query_chain: t.Optional[QueryChain], id_: Id, nullable: bool = False
            ) -> t.Optional[Row]:
        """
        Returns row of given id or raises a NotFound error.
        """
        if not query_chain or query_chain._is_trivial:
            # simple "get by id"
            result = self._table.get(doc_id=id_)
        else:
            # find the row in the filtered query
            filtered = self._resolve_filter(query_chain._reduced_filter)
            result = next((row for row in filtered if row.doc_id == id_), None)

        if result:
            return result
        elif nullable:
            return
        raise self.NotFound(id_=id_)

    def _resolve_exists(self, query_chain: QueryChain) -> bool:
        """Returns whether any row specified by the query exist."""
        filtered = self._resolve_filter(query_chain._reduced_filter)
        return bool(filtered)

    def _resolve_count(self, query_chain: QueryChain) -> int:
        """
        Counts rows filtering them out by the query specifying conditions that they should met.
        """
        filtered = self._resolve_filter(query_chain._reduced_filter)
        return len(filtered)

    def _resolve_update(self, query_chain: QueryChain, update: Row) -> Ids:
        """
        Updates all rows specified by the query with given update.
        """
        if query_chain._is_trivial:
            return self._table.update(update)
        return self._table.update(update, query_chain._reduced_filter)

    def _resolve_remove(self, query_chain: QueryChain) -> Ids:
        """
        Removes all rows specified by the query from the collection.

        NB: the command isn't atomic

        :raises: InvalidQueryError iff query is trivial. If you want to empty your collection,
        use `clear` instead.
        """
        if query_chain._is_trivial:
            raise InvalidQueryError
        result = self._table.remove(query_chain._reduced_filter)
        return result

    # dao commands

    def insert(self, row: Row) -> Id:
        """
        Inserts the row into the collection.

        :returns: id of the inserted row
        """
        return self._table.insert(row)

    def batch_insert(self, rows: Rows) -> Ids:
        """
        Inserts multiple rows into the collection.

        :returns: a iterable of ids
        """
        return tuple(self._table.insert_multiple(rows))

    def clear(self) -> None:
        """Clears the collection."""
        self._table.purge()
