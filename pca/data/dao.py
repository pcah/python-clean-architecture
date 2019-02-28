from abc import (
    ABC,
    abstractmethod,
)
from functools import reduce
from itertools import count
from operator import and_
import typing as t

from pca.interfaces.dao import (
    BatchOfDto,
    BatchOfKwargs,
    Dto,
    Id,
    Ids,
    IDao,
    IQueryChain,
    Kwargs,
)
from pca.utils.dependency_injection import Container, Scopes, scope

from .errors import QueryErrors
from .predicate import Predicate


class QueryChain(IQueryChain):
    """
    Technical detail of chaining queries.

    A proxy for a query interface of DAO, gathering lazy evaluated queries
    (ie. filter, sort, aggregate, etc) to call owning DAO to resolve them when non-lazy
    (ie. get, exists, count, update, etc) is called.
    """
    # TODO lazy queries: order_by, aggregate, annotate
    # TODO evaluating queries: slicing

    _ids: Ids = None
    _filters: t.List[Predicate] = None

    def __init__(self, dao: 'AbstractDao'):
        self._dao = dao

    @classmethod
    def _construct(
            cls, dao: 'AbstractDao', filters: t.List[Predicate] = None, ids: t.List[Id] = None
    ) -> 'QueryChain':
        """
        Technical detail of creating a new QueryChain with specified
        argument.
        """
        qc = cls(dao)
        qc._ids = ids
        qc._filters = filters
        return qc

    def _clone(self, filters: t.List[Predicate] = None, ids: t.List[Id] = None):
        """
        Technical detail of cloning current QueryChain object extended by an additional
        argument.
        """
        qc = self.__class__(self._dao)
        qc._ids = self._ids or ids
        if filters:
            qc._filters = (self._filters or []) + filters
        else:
            qc._filters = self._filters
        return qc

    def __repr__(self):
        return f"<QueryChain ids={self._ids}, filters={self._filters}>"

    @property
    def _is_trivial(self) -> bool:
        """Trivial QueryChain is the one that has no lazy operations defined."""
        return not (self._filters or self._ids)

    @property
    def _reduced_filter(self) -> t.Optional[Predicate]:
        """Before evaluation, sum up all filter predicates into a single one"""
        return None if self._is_trivial else reduce(and_, self._filters)

    # lazy queries

    def filter(self, predicate: Predicate) -> 'QueryChain':
        """
        Filters out objects by the predicate specifying conditions that they should met.
        """
        return self._clone(filters=[predicate])

    def filter_by(self, id_: Id = None, ids: Ids = None) -> 'QueryChain':
        """
        Filters objects by a single id or a iterable of ids.

        :raises: InvalidQueryError if:
            * both `id_` and `ids` arguments are defined
            * or the query is already filtered by id
        """
        if self._ids or bool(id_) == bool(ids):
            raise QueryErrors.CONFLICTING_QUERY_ARGUMENTS.with_params(id=id_, ids=ids)
        ids = ids or [id_]
        return self._clone(ids=ids)

    # evaluating queries

    def __iter__(self) -> Dto:
        """Yields values"""
        yield from self._dao._resolve_filter(self)

    def __len__(self) -> int:
        """Proxy for `count`."""
        return self.count()

    def get(self, id_: Id) -> t.Optional[Dto]:
        """Returns object of given id, or None iff not present."""
        qc = self.filter_by(id_=id_)
        filtered = self._dao._resolve_filter(qc)
        return self._dao._resolve_get(filtered, id_, nullable=True)

    def exists(self) -> bool:
        """Returns whether any object specified by the query exist."""
        return self._dao._resolve_exists(self)

    def count(self) -> int:
        """
        Counts objects filtering them out by the query specifying conditions that they
        should met.
        """
        return self._dao._resolve_count(self)

    # evaluating commands

    def update(self, **update) -> Ids:
        """
        Updates all objects specified by the query with given update.
        """
        return self._dao._resolve_update(self, update)

    def remove(self) -> Ids:
        """
        Removes all objects specified by the query from the collection.
        """
        return self._dao._resolve_remove(self)


class AbstractDao(IDao[Id], ABC):
    """Base abstract implementation for Data Access Object."""

    # lazy queries

    def all(self) -> QueryChain:
        """
        Returns a query chain representing all objects.

        Useful to explicitly denote counting, updating or removing all objects.
        """
        return QueryChain(self)

    def filter(self, predicate: Predicate) -> QueryChain:
        """
        Filters out objects by the predicate specifying conditions that they
        should met. Can be chained via `QueryChain` helper class.
        """
        return QueryChain._construct(self, filters=[predicate])

    def filter_by(self, id_: Id = None, ids: Ids = None) -> IQueryChain:
        """
        Filters objects by a single id or a iterable of ids.
        Can be chained with other queries via `IQueryChain` helper.

        :raises: InvalidQueryError iff both `id_` and `ids` arguments are defined.
        """
        if bool(id_) == bool(ids):
            raise QueryErrors.CONFLICTING_QUERY_ARGUMENTS.with_params(id=id_, ids=ids)
        ids = ids or [id_]
        return QueryChain._construct(self, ids=ids)

    # evaluating queries

    def get(self, id_: Id) -> t.Optional[Dto]:
        """
        Returns object of given id, or None iff not present.
        Shortcut for querying via `QueryChain.all`.
        """
        qc = QueryChain._construct(self, ids=[id_])
        filtered = self._resolve_filter(qc)
        return self._resolve_get(filtered, id_, nullable=True)

    @abstractmethod
    def _resolve_filter(self, query_chain: QueryChain) -> BatchOfDto:
        """Resolves filtering for any other resolving operation to compute."""

    @abstractmethod
    def _resolve_get(self, dtos: BatchOfDto, id_: Id, nullable: bool = False) -> t.Optional[Dto]:
        """Resolves `get`query described by the ids."""

    @abstractmethod
    def _resolve_exists(self, query_chain: QueryChain) -> bool:
        """Returns whether any object specified by the query exist."""

    @abstractmethod
    def _resolve_count(self, query_chain: QueryChain) -> int:
        """
        Counts objects filtering them out by the query specifying conditions that they should met.
        """

    # evaluating commands

    @abstractmethod
    def _resolve_update(self, query_chain: QueryChain, update: Kwargs) -> Ids:
        """
        Updates all objects specified by the query with given update.
        """

    @abstractmethod
    def _resolve_remove(self, query_chain: QueryChain) -> Ids:
        """
        Removes all objects specified by the query from the collection.
        """

    # instant commands

    @abstractmethod
    def insert(self, dto: Dto) -> Id:
        """
        Inserts the object into the collection.

        :returns: id of the inserted object
        """

    @abstractmethod
    def batch_insert(self, dtos: BatchOfDto) -> Ids:
        """
        Inserts multiple objects into the collection.

        :returns: a iterable of ids
        """

    @abstractmethod
    def clear(self) -> None:
        """Clears the collection."""


@scope(Scopes.SINGLETON)
class InMemoryDao(AbstractDao[int]):

    def __init__(self, container: Container, initial_content: BatchOfKwargs = None):
        self.container = container
        self._register: t.Dict[int, Dto] = {}
        self._id_generator = count(1)
        if initial_content:
            self.batch_insert(initial_content)

    def _get_id(self) -> int:
        return next(self._id_generator)

    def _resolve_filter(self, query_chain: QueryChain) -> BatchOfDto:
        if query_chain._filters:
            filter_ = query_chain._reduced_filter
            filtered: BatchOfDto = (
                dto for dto in self._register.values()
                if filter_(dto)
            )
        else:
            filtered = self._register.values()
        if query_chain._ids:
            filtered = (dto for dto in filtered if dto.id in query_chain._ids)
        return [dto for dto in filtered if dto]

    def _resolve_get(self, dtos: BatchOfDto, id_: Id, nullable: bool = False) -> t.Optional[Dto]:
        result = next((dto for dto in dtos if dto.id == id_), None)
        if result is not None:
            return result
        elif nullable:
            return
        raise QueryErrors.NOT_FOUND.with_params(id=id_)

    def _resolve_exists(self, query_chain: QueryChain) -> bool:
        filtered = self._resolve_filter(query_chain)
        return bool(filtered)

    def _resolve_count(self, query_chain: QueryChain) -> int:
        filtered = self._resolve_filter(query_chain)
        return len(filtered)

    def _resolve_update(self, query_chain: QueryChain, update: Kwargs) -> Ids:
        updated_dtos = (
            (dto.update(update), dto.id)
            for dto in self._resolve_filter(query_chain)
        )
        return [id_ for _, id_ in updated_dtos]

    def _resolve_remove(self, query_chain: QueryChain) -> Ids:
        if query_chain._is_trivial:
            raise QueryErrors.UNRESTRICTED_REMOVE
        dtos_to_remove = (
            self._register.pop(dto.id)
            for dto in self._resolve_filter(query_chain)
        )
        return [dto.id for dto in dtos_to_remove]

    def insert(self, **kwargs) -> Id:
        id_ = self._get_id()
        dto = Dto(kwargs)
        dto.__id__ = id_
        self._register[id_] = dto
        return id_

    def batch_insert(self, batch_kwargs: BatchOfKwargs) -> Ids:
        return tuple(self.insert(**kwargs) for kwargs in batch_kwargs)

    def clear(self) -> None:
        self._register.clear()
