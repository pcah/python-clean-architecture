# -*- coding: utf-8 -*-
import abc
import six

from dharma.data.traits import Mapping, Sequence, Type
from dharma.utils.inspect import get_all_subclasses
from dharma.utils.collections import get_duplicates


# noinspection PyProtectedMember
@six.add_metaclass(abc.ABCMeta)
class InMemoryRepository(object):
    """
    Repository implementation which holds the objects in memory.
    All instances of a repository for given `klass` will behave as Borgs:
    all share the same registry for instances of the klass.

    Method `load` is abstract and should be overridden with the proper
    implementation of the loading process. The method is expected to use
    `set` or `batch_set` methods to update the register of the repository.

    InMemoryRepository respects inheritance of the `klass`, so if there is
    created repository for the superclass of the `klass`, during loading it
    will have all the `klass` objects registered as well.
    """

    klass = Type()
    _register = Mapping()
    _klass_super_repos = Sequence()

    _ALL_REPOS = {}

    class NotFound(Exception):
        pass

    def __init__(self, klass):
        """
        :param klass: the class of target instances.
        """
        super(InMemoryRepository, self).__init__()
        self.klass = klass
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
                self.batch_set(subrepo.get_all(), unique=True)
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
        return "<{}: {}; id: {}>".format(
            self.__class__.__name__, self.klass.__name__, id(self))

    def get_by_id(self, id):
        """
        Returns object of given id.
        :raises: NotFound iff object of given id is not present.
        """
        try:
            return self._register[id]
        except KeyError:
            raise self.NotFound("Id '{}' in {} hasn't been found".format(
                id, self))

    def get_by_id_or_none(self, id):
        """Returns object of given id or None."""
        return self._register.get(id)

    def get_all(self):
        """Returns dictview with all the objects."""
        return self._register.values()

    def set(self, obj):
        assert isinstance(obj, self.klass)
        self._register[id(obj)] = obj

    def batch_set(self, objs, unique=False):
        assert not get_duplicates(obj.id for obj in objs)
        assert all(isinstance(obj, self.klass) for obj in objs)
        update = {o.id: o for o in objs}
        if unique:
            # objects should be uniquely
            common = set(update.keys()) & set(self._register.keys())
            assert not common, (
                "Duplicate item(s) detected in {}. Object ids already "
                "existing: {}"
            ).format(self, tuple(common))
        self._register.update(update)

    @abc.abstractmethod
    def load(self):
        """
        Abstract method to implement loading of the subjects to
        the repository. It should use `set` or `batch_set` to update
        own register.
        """
        raise NotImplemented

    def clear(self):
        """
        Clears content of the register of the instances. The registry is
        shared among all the repositories of the `klass`, so `clear` purges
        all the repositories.
        """
        # TODO remove the content of _register from super repos.
        self._register.clear()
