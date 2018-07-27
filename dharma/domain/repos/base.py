import abc
from typing import (
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
)

from dharma.data.formulae.predicate import Predicate
from dharma.exceptions import RepoError, RepoUpdateNotUniqueError
from dharma.utils.collections import get_duplicates


T = TypeVar('T')


class BaseRepository(Generic[T]):
    class NotFound(RepoError):
        """
        Error describing that an item hasn't been found on `get` call.
        """
        DEFAULT_CODE = 'NOT-FOUND'

    def __init__(self,
                 klass: Type[T] = None,  # flake8: noqa
                 factory: Callable[..., T] = None  # flake8: noqa
                 ) -> None:
        """
        :param klass: (optional) the class of target instances. Class
         `object` will be used iff not specified.
        :param factory: (optional) factory, a callable used to create objects
         of the klass. If specified, it will be called instead of klass.
        """
        self.klass = klass or object
        self.factory = factory

    def _get_id(self, obj: T) -> int:
        """
        Technical method, retrieving id from an `obj`. Override if needed.

        NB: Id is assumed to be `int`. I'm in favour of purely surrogate
        DB keys.
        """
        return obj.id

    def _set_id(self, obj: T, id: int) -> None:
        """
        Technical method, retrieving id from an `obj`. Override if needed.

        NB: Id is assumed to be `int`. I'm in favour of purely surrogate
        DB keys.
        """
        obj.id = id

    def create(self, *args, **kwargs) -> T:
        """
        Creates an object compatible with this repository. Uses repo's factory
        or the klass iff factory not present.

        NB: Does not inserts the object to the repository.
        Use `create_and_insert` method for that.

        :params *args, **kwargs: arguments for calling the factory.
        :returns: the object created.
        """
        factory = self.factory or self.klass
        return factory(*args, **kwargs)

    def create_and_insert(self, *args, **kwargs) -> T:
        """
        Creates an object compatible with this repository and inserts it. Uses
        repo's factory or the klass iff factory not present.

        :params *args, **kwargs: arguments for calling the factory.
        :returns: the object created.
        """
        obj = self.create(*args, **kwargs)
        self.insert(obj)
        return obj

    @abc.abstractmethod
    def get(self, id: int) -> T:
        """
        Returns object of given id or raises a class-specific error.

        :returns: object of given id.
        :raises: cls.NotFound iff object of given id is not present.
        """

    @abc.abstractmethod
    def get_or_none(self, id: int) -> Optional[T]:
        """Returns object of given id or None."""

    @abc.abstractmethod
    def exists(self, id: int) -> bool:
        """Returns whether id exists in the repo."""

    @abc.abstractmethod
    def filter(self, predicate: Predicate = None) -> List[T]:
        """
        Filters out objects in the register by the values in kwargs.

        :param predicate: Predicate: (optional) predicate specifing conditions
         that items should met. Iff no predicate is given, all objects should
         be returned.
        :returns: list of objects conforming given predicate.
        """
        # assert id not in predicate.get_vars(), (
        #     "Id's should be unique. If you want to get by id, use `get` "
        #     "method"
        # )

    @abc.abstractmethod
    def count(self, predicate: Optional[Predicate]) -> int:
        """
        Counts objects in the repo.

        :param predicate: Predicate: predicate specifing conditions that items
         should met. Iff no predicate is given, all objects should
         be counted.
        :returns: number of objects conforming given predicate.
        """

    @abc.abstractmethod
    def insert(self, obj: T) -> T:
        """
        Inserts the object into the repository. Specific behaviour
        should be implemented in subclasses.

        :param obj: an object to be put into the repository.
        :returns: the object
        """
        assert isinstance(obj, self.klass)
        assert not self.exists(self._get_id(obj))
        return obj

    @abc.abstractmethod
    def batch_insert(self, objs: Iterable[T]) -> List[T]:
        """
        Inserts collection of objects into the repository. Specific behaviour
        should be implemented in subclasses.

        :param objs: Iterable of objects intended for the repo.
        :returns: The payload: a dict of {id: obj}
        """
        payload = list(objs)
        assert all(isinstance(obj, self.klass) for obj in payload)
        return payload

    @abc.abstractmethod
    def update(self, obj: T) -> T:
        """
        Updates the object in the repository. Specific behaviour
        should be implemented in subclasses.

        :param obj: an object to be put into the repository.
        :returns: the object
        """
        assert isinstance(obj, self.klass)
        assert self.exists(self._get_id(obj))
        return obj

    @abc.abstractmethod
    def batch_update(self, objs: Iterable[T]) -> Dict[int, T]:
        """
        Updates objects gathered in the collection. Specific behaviour
        should be implemented in subclasses.

        :param objs: Iterable of objects intended to be updated.
        :returns: The payload: a dict of {id: obj}
        """
        payload = tuple(objs)
        assert not get_duplicates(self._get_id(obj) for obj in payload)
        assert all(isinstance(obj, self.klass) for obj in payload)
        payload = {self._get_id(obj): obj for obj in payload}
        # objects should be updated uniquely
        common = get_duplicates(self._get_id(obj) for obj in objs)
        if common:
            raise RepoUpdateNotUniqueError(common)
        return payload

    @abc.abstractmethod
    def remove(self, obj: T) -> bool:
        """
        Removes given object from the repo. Returns True iff done,
        False otherwise.
        """

    def batch_remove(self, objs: Iterable[T]) -> List[bool]:
        """Removes a collection of objects from the repo."""
        return List(self.remove(obj) for obj in objs)

    @abc.abstractmethod
    def pop(self, id: int) -> Optional[T]:
        """
        Removes an object specified by given id from the repo and returns it.
        Returns None iff not found.
        """

    def batch_pop(self, ids: Iterable[int]) -> List[T]:
        """
        Removes an object specified by given id from the repo and returns it.
        """
        return [self.pop(id_) for id_ in ids]
