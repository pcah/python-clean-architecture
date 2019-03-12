import typing as t

from pca.data.dao import (
    AbstractDao,
    BatchOfKwargs,
    BatchOfDto,
    Dto,
    Id,
    Ids,
    Kwargs,
    QueryChain,
)
from pca.data.errors import QueryErrors
from pca.utils.dependency_injection import Container

from .errors import IntegrationErrors

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
            raise IntegrationErrors.NOT_FOUND.with_params(target='tinydb')
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
            raise IntegrationErrors.NO_TABLE_NAME_PROVIDED

        if self._path:
            if self._path not in self._db_cache:
                self._db_cache[self._path] = tinydb.TinyDB(**kwargs)
            self._db: tinydb.TinyDB = self._db_cache[self._path]
        else:
            if 'storage' not in kwargs:
                kwargs['storage'] = tinydb.storages.MemoryStorage
            self._db = tinydb.TinyDB(**kwargs)
        self._table: tinydb.database.Table = self._db.table(self._table_name)

    def _resolve_filter(self, query_chain: QueryChain) -> BatchOfDto:
        """Resolves filtering for any other resolving operation to compute."""
        if query_chain._is_trivial:
            # none of filtering queries
            return self._table.all()
        if not query_chain._filters:
            # only ids as query
            return list(filter(
                None, (self._table.get(doc_id=id_) for id_ in query_chain._ids)
            ))
        filtered = self._table.search(query_chain._reduced_filter)
        if not query_chain._ids:
            # only filters as query
            return filtered
        # both
        return [dto for dto in filtered if dto.doc_id in query_chain._ids]

    def _resolve_get(self, dtos: BatchOfDto, id_: Id, nullable: bool = False) -> t.Optional[Dto]:
        """Resolves `get` query described by the ids."""
        result = next((dto for dto in dtos if dto.doc_id == id_), None)
        if result is not None:
            return result
        elif nullable:
            return
        raise QueryErrors.NOT_FOUND.with_params(id=id_)

    def _resolve_exists(self, query_chain: QueryChain) -> bool:
        """Returns whether any object specified by the query exist."""
        filtered = self._resolve_filter(query_chain)
        return bool(filtered)

    def _resolve_count(self, query_chain: QueryChain) -> int:
        """
        Counts objects filtering them out by the query specifying conditions that they should met.
        """
        filtered = self._resolve_filter(query_chain)
        return len(filtered)

    def _resolve_update(self, query_chain: QueryChain, update: Kwargs) -> Ids:
        """
        Updates all objects specified by the query with given update.

        NB: the command isn't atomic
        """
        if query_chain._is_trivial:
            return self._table.update(update)
        filtered = self._resolve_filter(query_chain)
        result = self._table.update(update, doc_ids=[d.doc_id for d in filtered])
        return result

    def _resolve_remove(self, query_chain: QueryChain) -> Ids:
        """
        Removes all objects specified by the query from the collection.

        NB: the command isn't atomic

        :raises: QueryError iff query is trivial. If you want to empty your collection,
        use `clear` instead.
        """
        if query_chain._is_trivial:
            raise QueryErrors.UNRESTRICTED_REMOVE
        filtered = self._resolve_filter(query_chain)
        result = self._table.remove(doc_ids=[d.doc_id for d in filtered])
        return result

    # dao commands

    def insert(self, **kwargs) -> Id:
        """
        Inserts the object into the collection.

        :returns: id of the inserted object
        """
        return self._table.insert(kwargs)

    def batch_insert(self, batch_kwargs: BatchOfKwargs) -> Ids:
        """
        Inserts multiple objects into the collection.

        :returns: a iterable of ids
        """
        return tuple(self._table.insert_multiple(batch_kwargs))

    def clear(self) -> None:
        """Clears the collection."""
        self._table.purge()
