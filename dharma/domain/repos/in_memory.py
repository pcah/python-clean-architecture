# -*- coding: utf-8 -*-
import typing as t
from collections import defaultdict

from dharma.data.formulae import Predicate
from dharma.utils.imports import get_dotted_path


from .base import BaseRepository, Id, T


_NOT_FOUND_MSG = "Id '{0}' in {1} hasn't been found"


class InMemoryRepository(BaseRepository, t.Generic[T]):
    """
    Repository implementation which holds the objects in memory.
    All instances of a repository for given `klass` will behave as Borgs:
    all share the same registry for instances of the klass.

    InMemoryRepository respects inheritance of the `klass`, so if there is
    created repository for the superclass of the `klass`, during loading it
    will have all the `klass` objects registered as well.
    """

    # {klass_qualname: {instance_id: instance}}
    _REGISTERS: t.DefaultDict[str, dict] = defaultdict(dict)

    class NotFound(BaseRepository.NotFound):
        pass

    def __init__(self,
                 klass: t.Type[T] = None,
                 factory: t.Callable[..., T] = None,
                 get_id: t.Callable[[T], int] = None,
                 ):
        super(InMemoryRepository, self).__init__(klass=klass, factory=factory, get_id=get_id)
        self._klass_qualname: str = get_dotted_path(klass)

    @classmethod
    def _clear_all_repos(cls):
        """
        Removes all registered repos from the _ALL_REPOS registery.
        This method is purposed to be called during test clean-ups.
        """
        for repo in cls._REGISTERS:
            repo.clear()

    def __repr__(self):
        return "<{0}: {1}; id: {2}>".format(
            self.__class__.__name__, self._klass.__name__, id(self))

    def get(self, id_: Id) -> T:
        """
        :returns: object of given id.
        :raises: NotFound iff object of given id is not present.
        """
        try:
            return self._REGISTERS[self._klass_qualname][id_]
        except KeyError:
            raise self.NotFound(_NOT_FOUND_MSG.format(id, self))

    def get_or_none(self, id_: Id) -> t.Optional[T]:
        """Returns object of given id or None."""
        return self._REGISTERS[self._klass_qualname].get(id_)

    def get_all(self) -> t.Iterable[T]:
        """Returns dictview with all the objects."""
        return list(self._REGISTERS[self._klass_qualname].values())

    def exists(self, id_: Id) -> bool:
        """Returns whether id exists in the repo."""
        return id_ in self._REGISTERS[self._klass_qualname]

    def count(self, predicate: Predicate=None) -> int:
        if not predicate:
            return len(self._REGISTERS[self._klass_qualname])
        filtered = self.filter(predicate)
        return len(filtered)

    def filter(self, predicate: Predicate = None) -> t.List[T]:
        """
        Filters out objects in the register by the values in kwargs.

        :param predicate: Predicate: (optional) predicate specifing conditions
         that items should met. Iff no predicate is given, all objects should
         be returned.
        :returns: list of objects conforming given predicate.
        """
        if not predicate:
            return list(self._REGISTERS[self._klass_qualname].values())
        return [obj for obj in self._REGISTERS[self._klass_qualname].values() if predicate(obj)]

    def insert(self, obj: T) -> T:
        """
        Inserts the object into the repository.

        :param obj: an object to be put into the repository.
        :returns: the object
        """
        super(InMemoryRepository, self).insert(obj)
        self._REGISTERS[self._klass_qualname][self._get_id(obj)] = obj
        # for super_repo in self._klass_super_repos:
        #     # TODO this doesn't concern duplicates of ids in super_repo
        #     super_repo._register[obj.id] = obj
        return obj

    def batch_insert(self, objs: t.Iterable[T]):
        """
        Inserts collection of objects into the repository.

        :param objs: Iterable of objects intended for the repo.
        :returns: The payload: a dict of {id: obj}
        """
        super(InMemoryRepository, self).batch_insert(objs)
        for obj in objs:
            self.insert(obj)

    def update(self, obj: T) -> bool:
        """
        Updates the object in the repository.

        :param obj: an object to be put into the repository.
        :returns: the object
        """
        super(InMemoryRepository, self).update(obj)
        self._REGISTERS[self._klass_qualname][self._get_id(obj)] = obj
        return True

    def batch_update(self, objs: t.Iterable[T]) -> t.Dict[Id, bool]:
        """
        Updates objects gathered in the collection.

        :param objs: Iterable of objects intended to be updated.
        :returns: a dict of {id: obj}
        """
        payload = super(InMemoryRepository, self).batch_update(objs)
        return {self._get_id(obj): self.update(obj) for obj in payload}

    def remove(self, obj: T):
        """Removes given object from the repo."""
        id_ = self._get_id(obj)
        try:
            self._REGISTERS[self._klass_qualname].pop(id_)
        except KeyError:
            raise self.NotFound(_NOT_FOUND_MSG.format(id_, self))

    def pop(self, id_: Id) -> T:
        """
        Removes an object specified by given id from the repo and returns it.
        """
        try:
            return self._REGISTERS[self._klass_qualname].pop(id_)
        except KeyError:
            raise self.NotFound(_NOT_FOUND_MSG.format(id_, self))
