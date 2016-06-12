# -*- coding: utf-8 -*-
from dharma.utils.inspect import get_all_subclasses
from dharma.utils.sentinel import Sentinel

from .base import BaseRepository


unknown_value = Sentinel(module='dharma.domain.repos', name='unknown_value')


# noinspection PyProtectedMember
class InMemoryRepository(BaseRepository):
    """
    Repository implementation which holds the objects in memory.
    All instances of a repository for given `klass` will behave as Borgs:
    all share the same registry for instances of the klass.

    InMemoryRepository respects inheritance of the `klass`, so if there is
    created repository for the superclass of the `klass`, during loading it
    will have all the `klass` objects registered as well.
    """

    _register = {}
    _klass_super_repos = []

    _ALL_REPOS = {}

    class NotFound(BaseRepository.NotFound):
        pass

    def __init__(self, klass=None, factory=None):
        super(InMemoryRepository, self).__init__(klass=klass, factory=factory)
        self._register = {}
        repositories = self.__class__._ALL_REPOS
        id_ = id(klass)
        if id_ in repositories:
            # there are repository instances for this class already
            # make them Borg-like with respect to _registers
            leader = repositories[id_]
            self._register = leader._register
            self._klass_super_repos = leader._klass_super_repos
        else:
            # a new klass
            self._register = {}
            # look for super-repos
            self._klass_super_repos = self._find_super_repos(klass)
            for subrepo in self._find_sub_repos(klass):
                # ... register this repo at the sub-repos as a super-repo...
                subrepo._klass_super_repos.append(self)
                # ... and accept their instances as own
                self.batch_save(subrepo.get_all(), unique=True)
            repositories[id_] = self  # set self as the Borg leader

    @classmethod
    def _find_super_repos(cls, klass):
        """Searching repositories for superclasses of the `klass`"""
        ids = (
            id(superklass) for superklass in klass.mro()
            if id(superklass) in cls._ALL_REPOS
        )
        return [cls._ALL_REPOS[id_] for id_ in ids]

    @classmethod
    def _find_sub_repos(cls, klass):
        """Searching repositories for subclasses of the `klass`"""
        ids = (id(subcls) for subcls in get_all_subclasses(klass))
        return (
            cls._ALL_REPOS[id_] for id_ in ids
            if id_ in cls._ALL_REPOS
        )

    @classmethod
    def _clear_all_repos(cls):
        """
        Removes all registered repos from the _ALL_REPOS registery.
        This method is purposed to be called during test clean-ups.
        """
        cls._ALL_REPOS.clear()

    def __repr__(self):
        return "<{0}: {1}; id: {2}>".format(
            self.__class__.__name__, self.klass.__name__, id(self))

    def get(self, id):
        """
        :returns: object of given id.
        :raises: NotFound iff object of given id is not present.
        """
        try:
            return self._register[id]
        except KeyError:
            raise self.NotFound("Id '{0}' in {1} hasn't been found".format(
                id, self))

    def get_or_none(self, id):
        """Returns object of given id or None."""
        return self._register.get(id)

    def get_all(self):
        """Returns dictview with all the objects."""
        return self._register.values()

    def exists(self, id):
        """Returns whether id exists in the repo."""
        return id in self._register

    def filter(self, **kwargs):
        """
        Filters out objects in the register by the values in kwargs.

        :param **kwargs: dictionary of attributes which should be conformed
         by all of the objects returned
        :returns: list of objects conforming specified kwargs
        """
        super(InMemoryRepository, self).filter(**kwargs)
        result = self._register.values()
        for key, value in kwargs.items():
            result = [
                obj for obj in result
                if getattr(obj, key, unknown_value) == value
            ]
            if not result:
                return result
        return result

    def save(self, obj):
        """
        Sets the object into the repository.

        :param obj: an object to be put into the repository.
        :returns: the object
        """
        super(InMemoryRepository, self).save(obj)
        self._register[id(obj)] = obj
        for super_repo in self._klass_super_repos:
            # TODO this doesn't concern duplicates of ids in super_repo
            super_repo._register[id(obj)] = obj
        return obj

    def batch_save(self, objs, unique=False):
        """
        Sets collection of objects into the repository.

        :param objs: Iterable of objects intended for the repo.
        :param unique: Boolean that turns on validation of unique id's before
         putting into the repo.
        :returns: sequence of (id, obj) 2-tuples
        """
        update = super(InMemoryRepository, self).batch_save(
            objs, unique=unique)
        self._register.update(update)
        for super_repo in self._klass_super_repos:
            # TODO this doesn't concern duplicates of ids in super_repo
            super_repo._register.update(update)
        return update

    def clear(self):
        """
        Clears content of the register of the instances. The registry is
        shared among all the repositories of the `klass`, so `clear` purges
        all the repositories.
        """
        # TODO remove the content of _register from super repos.
        self._register.clear()

    def remove(self, obj):
        """Removes given object from the repo."""
        self._register.pop(obj.id)

    def pop(self, id):
        """
        Removes an object specified by given id from the repo and returns it.
        """
        return self._register.pop(id)
