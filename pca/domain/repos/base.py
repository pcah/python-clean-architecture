import abc
import typing as t
from operator import attrgetter

from pca.data.formulae.predicate import Predicate
from pca.exceptions import RepoError, RepoUpdateNotUniqueError
from pca.utils.collections import get_duplicates
from pca.utils.operators import error_catcher

Id = t.NewType('Id', int)
T = t.TypeVar('T')


class BaseRepository(t.Generic[T]):

    class NotFound(RepoError):
        """
        Error describing that an item hasn't been found on `get` call.
        """
        DEFAULT_CODE = 'NOT-FOUND'

    def __init__(self,
                 klass: t.Type[T],
                 factory: t.Callable[..., T] = None,
                 get_id: t.Callable[[T], int] = None,
                 ) -> None:
        """
        :param klass: the class of target instances.
        :param factory: (optional) factory, a callable used to create objects
         of the klass. If specified, it will be called instead of klass.
        :param get_id: (optional) a function to get ID of the `klass` instance
         If not provided, a default of `attrgetter('id')` will be used.
        """
        self._klass = klass
        self._factory = factory or klass
        self._get_id = get_id or attrgetter('id')

    def create(self, *args, **kwargs) -> T:
        """
        Creates an object compatible with this repository. Uses repo's factory
        or the klass iff factory not present.

        NB: Does not inserts the object to the repository.
        Use `create_and_insert` method for that.

        :params *args, **kwargs: arguments for calling the factory.
        :returns: the object created.
        """
        return self._factory(*args, **kwargs)

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
    def get(self, id_: Id) -> T:
        """
        Returns object of given id or raises a class-specific error.

        :returns: object of given id.
        :raises: cls.NotFound iff object of given id is not present.
        """

    @abc.abstractmethod
    def get_or_none(self, id_: Id) -> t.Optional[T]:
        """Returns object of given id or None."""

    @abc.abstractmethod
    def all(self) -> t.Iterable[T]:
        """Returns a list with all the objects."""

    @abc.abstractmethod
    def exists(self, id_: Id) -> bool:
        """Returns whether id exists in the repo."""

    @abc.abstractmethod
    def filter(self, predicate: Predicate) -> t.List[T]:
        """
        Filters out objects in the register by the values in kwargs.

        :param predicate: predicate specifying conditions that items should
         met. Iff no predicate is given, all objects should be returned.
        :returns: list of objects conforming given predicate.
        """
        # assert id not in predicate.get_vars(), (
        #     "Id's should be unique. If you want to get by id, use `get` "
        #     "method"
        # )

    @abc.abstractmethod
    def count(self, predicate: t.Optional[Predicate]) -> int:
        """
        Counts objects in the repo.

        :param predicate: Predicate: predicate specifying conditions that items
         should met. Iff no predicate is given, all objects should
         be counted.
        :returns: number of objects conforming given predicate.
        """

    @abc.abstractmethod
    def insert(self, obj: T) -> bool:
        """
        Inserts the object into the repository. Specific behaviour
        should be implemented in subclasses.

        :param obj: an object to be put into the repository.
        :returns: whether insert operation was successful
        """
        assert isinstance(obj, self._klass)
        assert not self.exists(self._get_id(obj))
        return True

    def batch_insert(self, objs: t.Iterable[T]) -> t.Dict[Id, bool]:
        """
        Inserts collection of objects into the repository.

        :param objs: Iterable of objects intended for the repo.
        :returns: a dict of {id: was_insert_successful}
        """
        error_classes = (AssertionError, self.NotFound)
        return {
            self._get_id(obj): error_catcher(error_classes, self.insert, obj)
            for obj in objs
        }

    @abc.abstractmethod
    def update(self, obj: T) -> bool:
        """
        Updates the object in the repository. Specific behaviour
        should be implemented in subclasses.

        :param obj: an object to be put into the repository.
        :returns: whether update operation was successful
        """
        assert isinstance(obj, self._klass)
        assert self.exists(self._get_id(obj))
        return True

    def batch_update(self, objs: t.Iterable[T]) -> t.Dict[Id, bool]:
        """
        Updates objects gathered in the collection.

        :param objs: Iterable of objects intended to be updated.
        :returns: a dict of {id: was_update_successful}
        """
        assert not get_duplicates(self._get_id(obj) for obj in objs)
        assert all(isinstance(obj, self._klass) for obj in objs)
        # objects should be updated uniquely
        common = get_duplicates(self._get_id(obj) for obj in objs)
        if common:
            raise RepoUpdateNotUniqueError(common)

        error_classes = (AssertionError, self.NotFound)
        return {
            self._get_id(obj): error_catcher(error_classes, self.update, obj)
            for obj in objs
        }

    @abc.abstractmethod
    def remove(self, obj: T) -> bool:
        """
        Removes given object from the repo. Specific behaviour
        should be implemented in subclasses.
        """

    def batch_remove(self, objs: t.Iterable[T]) -> t.Dict[Id, bool]:
        """Removes a collection of objects from the repo."""
        error_classes = (AssertionError, self.NotFound)
        return {
            self._get_id(obj): error_catcher(error_classes, self.remove, obj)
            for obj in objs
        }

    @abc.abstractmethod
    def pop(self, id_: Id) -> t.Optional[T]:
        """
        Removes an object specified by given id from the repo and returns it.
        Returns None iff not found. Specific behaviour should be implemented
        in subclasses.
        """

    def batch_pop(self, ids: t.Iterable[Id]) -> t.Dict[Id, T]:
        """
        Removes an object specified by given id from the repo and returns it.
        """
        return {id_: self.pop(id_) for id_ in ids}
