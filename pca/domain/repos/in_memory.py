# -*- coding: utf-8 -*-
import typing as t
from collections import defaultdict

from pca.data.formulae import Predicate
from pca.utils.collections import iterate_over_values
from pca.utils.functools import reify
from pca.utils.imports import get_dotted_path
from pca.utils.operators import error_catcher
from pca.utils.serialization import load_from_filepath

from .base import BaseRepository, Id, T


_NO_REPOSITORY_MSG = "No repository for {} has been found"
_NOT_FOUND_MSG = "Id '{}' in {} hasn't been found"


class InMemoryRepository(BaseRepository, t.Generic[T]):
    """
    Repository implementation which holds the objects in memory.
    InMemoryRepository respects inheritance of the `klass`, so if there is
    created repository for the superclass of the `klass`, during loading it
    will have all the `klass` objects registered as well.
    """

    # {klass_qualname: {instance_id: instance}}
    _REGISTERS: t.Dict[str, dict] = {}
    # {klass_qualname: [list, of, its, super-repos]
    _SUPER_KLASSES_WITH_REPO: t.DefaultDict[str, list] = defaultdict(list)

    class NotFound(BaseRepository.NotFound):
        pass

    def __init__(self,
                 klass: t.Type[T],
                 factory: t.Callable[..., T] = None,
                 get_id: t.Callable[[T], int] = None,
                 ):
        super().__init__(klass=klass, factory=factory, get_id=get_id)
        self._klass_qualname: str = get_dotted_path(klass)
        if self._klass_qualname not in self._SUPER_KLASSES_WITH_REPO:
            self._SUPER_KLASSES_WITH_REPO[self._klass_qualname] = [
                get_dotted_path(k)
                for k in klass.mro()
                if get_dotted_path(k) in self._REGISTERS
            ]
        if self._klass_qualname not in self._REGISTERS:
            self._REGISTERS[self._klass_qualname] = {}

    @classmethod
    def _clear_all_repos(cls):
        """
        Removes all registered repos from the _ALL_REPOS registry.
        This method is purposed to be called during test clean-ups.
        """
        for repo in cls._REGISTERS.values():
            repo.clear()

    @classmethod
    def register_klass(cls, klass: t.Type[T]) -> t.Type[T]:  # pragma: no cover
        """
        Decorates a class to be recognized by InMemoryRepository as a target
        of a repository.
        """
        cls._REGISTERS[get_dotted_path(klass)] = {}
        return klass

    @classmethod
    def load_from_filepath(cls, filepath):
        result = load_from_filepath(filepath)
        repos = {}
        for obj in iterate_over_values(result):
            klass = obj.__class__
            if klass not in repos:
                repos[klass] = cls(klass)
            repos[klass].insert(obj)

    def __repr__(self):
        return "<{0}: {1}; id: {2}>".format(
            self.__class__.__name__, self._klass.__name__, id(self))

    @reify
    def klass_register(self):
        try:
            return self._REGISTERS[self._klass_qualname]
        except KeyError as e:  # pragma: no cover
            raise self.NotFound(_NO_REPOSITORY_MSG.format(self._klass_qualname)) from e

    def get(self, id_: Id) -> T:
        """
        :returns: object of given id.
        :raises: NotFound iff object of given id is not present.
        """
        try:
            return self.klass_register[id_]
        except KeyError as e:
            raise self.NotFound(_NOT_FOUND_MSG.format(id, self)) from e

    def get_or_none(self, id_: Id) -> t.Optional[T]:
        """Returns object of given id or None."""
        return self.klass_register.get(id_)

    def all(self) -> t.List[T]:
        """Returns a list of all the objects."""
        return list(self.klass_register.values())

    def exists(self, id_: Id) -> bool:
        """Returns whether id exists in the repo."""
        return id_ in self.klass_register

    def count(self, predicate: Predicate=None) -> int:
        if not predicate:
            return len(self.klass_register)
        filtered = self.filter(predicate)
        return len(filtered)

    def filter(self, predicate: Predicate) -> t.List[T]:
        """
        Filters out objects in the register by the values in kwargs.

        :param predicate: (optional) predicate specifing conditions
         that items should met. Iff no predicate is given, all objects should
         be returned.
        :returns: list of objects conforming given predicate.
        """
        return [obj for obj in self.klass_register.values() if predicate(obj)]

    def insert(self, obj: T) -> bool:
        """
        Inserts the object into the repository.

        :param obj: an object to be put into the repository.
        :returns: the object
        """
        super().insert(obj)
        id_ = self._get_id(obj)
        self.klass_register[id_] = obj
        for super_klass_qualname in self._SUPER_KLASSES_WITH_REPO[self._klass_qualname]:
            assert id_ not in self._REGISTERS[super_klass_qualname], \
                "Id conflict in super repos"
            self._REGISTERS[super_klass_qualname][id_] = obj
        return True

    def update(self, obj: T) -> bool:
        """
        Updates the object in the repository.

        :param obj: an object to be put into the repository.
        :returns: True iff object has been changed
        """
        super().update(obj)
        self.klass_register[self._get_id(obj)] = obj
        return True

    def batch_update(self, objs: t.Iterable[T]) -> t.Dict[Id, bool]:
        """
        Updates objects gathered in the collection.

        :param objs: Iterable of objects intended to be updated.
        :returns: a dict of {id: obj}
        """
        super().batch_update(objs)
        error_classes = (AssertionError, self.NotFound)
        return {
            self._get_id(obj): error_catcher(error_classes, self.update, obj)
            for obj in objs
        }

    def remove(self, obj: T):
        """Removes given object from the repo."""
        id_ = self._get_id(obj)
        try:
            self.klass_register.pop(id_)
        except KeyError:
            raise self.NotFound(_NOT_FOUND_MSG.format(id_, self))

    def pop(self, id_: Id) -> T:
        """
        Removes an object specified by given id from the repo and returns it.
        """
        try:
            return self.klass_register.pop(id_)
        except KeyError:
            raise self.NotFound(_NOT_FOUND_MSG.format(id_, self))
