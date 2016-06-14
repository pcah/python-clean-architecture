import abc
import six

from dharma.data.exceptions import DharmaError
from dharma.utils.collections import get_duplicates


@six.add_metaclass(abc.ABCMeta)
class BaseRepository(object):

    class NotFound(DharmaError):
        pass

    def __init__(self, klass=None, factory=None):
        """
        :param klass: the class of target instances. Class `object` will be
         used iff not specified.
        :param factory: optional factory, a callable used to create objects
         of the klass. If specified, it will be called instead of klass.
        """
        self.klass = klass or object
        self.factory = factory

    def create(self, *args, **kwargs):
        """
        Creates an object compatible with this repository. Uses repo's factory
        or the klass iff factory not present.

        NB: Does not save the object to the repository. Use `create_and_save`
        method for that.

        :params *args, **kwargs: arguments for calling the factory.
        :returns: the object created.
        """
        factory = self.factory or self.klass
        return factory(*args, **kwargs)

    def create_and_save(self, *args, **kwargs):
        """
        Creates an object compatible with this repository and saves it. Uses
        repo's factory or the klass iff factory not present.

        :params *args, **kwargs: arguments for calling the factory.
        :returns: the object created.
        """
        obj = self.create(*args, **kwargs)
        self.save(obj)
        return obj

    @abc.abstractmethod
    def get(self, id):
        """
        Returns object of given id or raises a class-specific error.

        :returns: object of given id.
        :raises: cls.NotFound iff object of given id is not present.
        """

    @abc.abstractmethod
    def get_or_none(self, id):
        """Returns object of given id or None."""

    @abc.abstractmethod
    def exists(self, id):
        """Returns whether id exists in the repo."""

    @abc.abstractmethod
    def filter(self, **kwargs):
        """
        Filters out objects in the register by the values in kwargs.

        :param **kwargs: dictionary of attributes which should be conformed
         by all of the objects returned
        :returns: list of objects conforming specified kwargs
        """
        assert id not in kwargs, (
            "Id's should be unique. If you want to get by id, use `get` "
            "method"
        )

    @abc.abstractmethod
    def count(self, **kwargs):
        """
        Counts objects in the repo.

        :param **kwargs: kwargs that will be used to filter objects in repo
         (the same way `filter` does).
        :returns: number of objects after filtering the repo by the kwargs.
        """

    @abc.abstractmethod
    def save(self, obj):
        """
        Sets the object into the repository. Specific behaviour
        should be implemented in subclasses.

        :param obj: an object to be put into the repository.
        :returns: the object
        """
        assert isinstance(obj, self.klass)
        return obj

    @abc.abstractmethod
    def batch_save(self, objs, unique=False):
        """
        Sets collection of objects into the repository. Specific behaviour
        should be implemented in subclasses.

        :param objs: Iterable of objects intended for the repo.
        :param unique: Boolean that turns on validation of unique id's before
         putting into the repo.
        :returns: sequence of (id, obj) 2-tuples
        """
        assert not get_duplicates(obj.id for obj in objs)
        assert all(isinstance(obj, self.klass) for obj in objs)
        update = dict((o.id, o) for o in objs)
        if unique:
            # objects should be uniquely
            common = set(update.keys()) & set(self._register.keys())
            assert not common, (
                "Duplicate item(s) detected in {}. Object ids already "
                "existing: {}"
            ).format(self, tuple(common))
        return update

    @abc.abstractmethod
    def remove(self, obj):
        """Removes given object from the repo."""

    def batch_remove(self, objs):
        """Removes a collection of objects from the repo."""
        for obj in objs:
            self.remove(obj)

    @abc.abstractmethod
    def pop(self, id):
        """
        Removes an object specified by given id from the repo and returns it.
        """

    def batch_pop(self, ids):
        """
        Removes an object specified by given id from the repo and returns it.
        """
        return [self.pop(id_) for id_ in ids]
