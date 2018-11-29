# -*- coding: utf-8 -*-
import abc
import typing as t


Id = t.TypeVar('Id')
Predicate = t.TypeVar('Predicate')
Row = t.Mapping[str, t.Any]


class IDao:
    """
    Interface for Data Access Object. Describes an abstraction over any kind
    of collections of rows of data: both relational database's tables and
    non-relational document sets, etc.
    """

    # TODO NotFound and other errors? are they implementation-specific?

    @abc.abstractmethod
    def get(self, id_: Id) -> Row:
        """
        Returns row of given id or raises a class-specific error.

        :raises: NotFound iff row of given id is not present.
        """

    @abc.abstractmethod
    def get_or_none(self, id_: Id) -> t.Optional[Row]:
        """Returns row of given id or None."""

    @abc.abstractmethod
    def all(self) -> t.Iterable[Row]:
        """Returns an iterable of all rows."""

    @abc.abstractmethod
    def exists(self, predicate: Predicate) -> bool:
        """Returns whether rows described by the predicate exist."""

    @abc.abstractmethod
    def count(self, predicate: Predicate = None) -> int:
        """
        Counts rows filtering them out by the predicate specifying
        conditions that they should met. Iff no predicate is given,
        all rows should be counted.
        """

    @abc.abstractmethod
    def filter(self, predicate: Predicate) -> t.Iterable[Row]:
        """
        Filters out rows by the predicate specifying conditions that they
        should met.
        """

    @abc.abstractmethod
    def insert(self, row: Row) -> bool:
        """
        Inserts the row into the collection.

        # TODO does it :raises: errors?
        # TODO or :returns: whether insert operation was successful?
        """

    @abc.abstractmethod
    def batch_insert(self, mappings: t.Iterable[Row]) -> t.Iterable[t.Tuple[Id, bool]]:
        """
        Inserts the row into the collection.

        :returns: a iterable of (id, was_insert_successful)
        """

    @abc.abstractmethod
    def update(self, id_: Id, row: Row) -> bool:
        """
        Updates the row in the collection.

        # TODO does it :raises: errors?
        # TODO or :returns: whether insert operation was successful?
        """

    @abc.abstractmethod
    def batch_update(self, rows: t.Mapping[Id, Row]) -> t.Dict[Id, bool]:
        """
        Updates rows gathered in the collection.

        :returns: a dict of {id: was_insert_successful}
        """

    @abc.abstractmethod
    def remove(self, id_: Id) -> bool:
        """
        Removes given row from the collection.

        # TODO does it :raises: errors?
        # TODO or :returns: whether insert operation was successful?
        """

    @abc.abstractmethod
    def batch_remove(self, id_: Id) -> t.Dict[Id, bool]:
        """
        Removes given row from the collection.

        :returns: a dict of {id: was_insert_successful}
        """

    @abc.abstractmethod
    def pop(self, predicate: Predicate) -> Row:
        """
        Removes an row specified by given id from the collection and returns it.

        :raises: NotFound iff row of given id is not present.
        """

    @abc.abstractmethod
    def batch_pop(self, predicate: Predicate) -> Row:
        """
        Removes an row specified by given id from the collection and returns it.
        """

    @abc.abstractmethod
    def clear(self) -> None:
        """
        Clears the collection.

        # TODO does it :raises: errors?
        """
