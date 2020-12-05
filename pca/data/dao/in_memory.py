import typing as t

from itertools import count

from pca.data.errors import QueryErrors
from pca.interfaces.dao import (
    BatchOfDto,
    BatchOfKwargs,
    Dto,
    Id,
    Ids,
    Kwargs,
)
from pca.utils.dependency_injection import (
    Scopes,
    scope,
)

from .abstract import (
    AbstractDao,
    QueryChain,
)


@scope(Scopes.SINGLETON)
class InMemoryDao(AbstractDao[int]):
    def __init__(self, initial_content: BatchOfKwargs = None):
        self._register: t.Dict[int, Dto] = {}
        self._id_generator = count(1)
        if initial_content:
            self.batch_insert(initial_content)

    def _get_id(self) -> int:
        return next(self._id_generator)

    def _resolve_filter(self, query_chain: QueryChain) -> BatchOfDto:
        if query_chain._filters:
            filter_ = query_chain._reduced_filter
            filtered: BatchOfDto = (dto for dto in self._register.values() if filter_(dto))
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
        updated_dtos = ((dto.update(update), dto.id) for dto in self._resolve_filter(query_chain))
        return [id_ for _, id_ in updated_dtos]

    def _resolve_remove(self, query_chain: QueryChain) -> Ids:
        if query_chain._is_trivial:
            raise QueryErrors.UNRESTRICTED_REMOVE
        dtos_to_remove = (self._register.pop(dto.id) for dto in self._resolve_filter(query_chain))
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
