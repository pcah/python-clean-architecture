"""
Some common interfaces.
"""
import typing as t

from pca.data.formulae import Predicate


class IRequest:
    """
    Interface for a facade which represents a request.
    Largely depends on a complete implementation.
    """


class IDao:
    """
    Interface for a data access object (aka DAO).
    """
    def get(self, predicate: Predicate):
        """Returns an entry described with the predicate"""

    def exists(self, predicate: Predicate):
        """True iff an entry exists"""


class ISession:
    """
    Interface for a session of a user (whatever that means for your
    application) and his local storage.
    """
    user: t.Any
