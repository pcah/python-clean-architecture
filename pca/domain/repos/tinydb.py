# -*- coding: utf-8 -*-
from typing import Callable, Generic, Optional, TypeVar

from pca.compat.db import tinydb
from pca.exceptions import DharmaConfigError
from pca.utils.imports import get_dotted_path
from .base import BaseRepository


T = TypeVar('T')


class TinyDbRepository(BaseRepository, Generic[T]):
    _table_name = None
    _table = None

    def __init__(self, engine_config: dict, serializer: Callable[[T], dict],
                 klass: T=None, factory: Callable[[dict], T]=None) -> None:
        if not tinydb:
            raise DharmaConfigError
        super(TinyDbRepository, self).__init__(klass=klass, factory=factory)
        self._table_name = get_dotted_path(klass)
        self.engine = tinydb.TinyDB(**engine_config)
        self._table = self.engine.table(self._table_name)

    def get(self, id: int) -> T:
        data = self._table.get(eid=id)
        if not data:
            raise self.NotFound
        return self.create(**data)

    def get_or_none(self, id: int) -> Optional(T):
        data = self._table.get(eid=id)
        return self.create(**data) if data is not None else None

    def save(self, obj: T) -> int:
        pass

    def clear(self) -> None:
        self._table.purge()
