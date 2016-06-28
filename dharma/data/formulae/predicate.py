"""
Contains the querying interface.
Starting with :class:`Var` you can construct complex
queries:
>>> ((where('f1') == 5) & (where('f2') != 2)) | where('s').matches(r'^\w+$')
(('f1' == 5) and ('f2' != 2)) or ('s' ~= ^\w+$ )
Predicates are executed by using the ``__call__``:
>>> q = where('val') == 5
>>> q({'val': 5})
True
>>> q({'val': 1})
False
"""
from enum import Enum
import re
from typing import (
    Any,
    Callable,
    Iterable,
)

from dharma.utils.collections import freeze, is_iterable
from dharma.utils.compare import eq


class Operation(Enum):
    # algebraic ops
    EQ = '=='
    NE = '!='
    LT = '<'
    LE = '<='
    GT = '>'
    GE = '>='

    # db-like ops
    EXISTS = 'exists'
    MATCHES = 'matches'
    SEARCH = 'search'
    TEST = 'test'

    # logical ops
    NOT = 'not'
    AND = 'and'
    OR = 'or'
    ANY = 'any'
    ALL = 'all'


def resolve_path(
        test: Callable[[Any], bool],
        path: Iterable[str]
        ) -> Callable[[Any], bool]:
    """
    Args:
        test:
        path:

    Returns:

    """
    def resolve_path_curried(value):
        for part in path:
            try:
                value = getattr(value, part)
            except AttributeError:
                try:
                    value = value[part]
                except (KeyError, TypeError):
                    return False
        return test(value)
    return resolve_path_curried


class Predicate(object):
    """
    Enwraps the actual condition function, which is run when the
    predicate is evaluated by calling its object. Predicates can be combined
    with logical and/or and modified with logical not.
    """
    def __init__(self, test, definition):
        self.test = test
        self.definition = definition

    def __call__(self, value):
        return self.test(value)

    def __hash__(self):
        return hash(self.definition)

    def __repr__(self):
        return 'Predicate{0}'.format(self.definition)

    def __eq__(self, other):
        return self.definition == other.definition

    # --- Associativity of Predicates

    def __and__(self, other):
        # We use a frozenset for the definitions as the AND operation is
        # commutative: (a | b == b | a)
        return Predicate(
            lambda value: self(value) and other(value),
            (Operation.AND, frozenset([self.definition, other.definition]))
        )

    def __or__(self, other):
        # We use a frozenset for the definitions as the OR operation is
        # commutative: (a & b == b & a)
        return Predicate(
            lambda value: self(value) or other(value),
            (Operation.OR, frozenset([self.definition, other.definition]))
        )

    def __invert__(self):
        return Predicate(
            lambda value: not self(value),
            (Operation.NOT, self.definition)
        )


class Var(object):
    """
    Represents a logic variable. Its primary use is a Predicate factory class:
    methods(ie. all, any, search, exists, test) return Predicate instances.

    Variables can be used to build predicates. There are two main ways of
    using predicates to query:
    1) ORM-like usage:
    >>> User = Var('user')
    >>> find(User.name == 'John Doe')
    >>> find(User['logged-in'] == True)
    2) SQL-like usage:
    >>> find(where('value') == True)

    Note that ``where(...)`` is a shorthand for ``Var(...)``, ie. creates
    an anonymous variable.

    Queries are executed by calling the Predicate object. They expect to get
    the element to test as the first argument and return ``True`` or ``False``
    depending on whether the elements matches the predicate or not.
    """

    def __init__(self, path=None):
        if path is None:
            self.path = ()
        elif is_iterable(path):
            self.path = tuple(path)
        else:
            self.path = (path,)

    def __getattr__(self, item):
        return Var(self.path + (item,))

    __getitem__ = __getattr__

    def _build_predicate(self, test, definition):
        """
        Generate a Predicate object based on a test function.
        :param test: The test the Predicate executes.
        :param definition: The definition of the Predicate.
        :return: A :class:`Predicate` object
        """
        if not self.path:
            raise ValueError('Var has no path')
        return Predicate(resolve_path(test, self.path), definition)

    def __eq__(self, rhs):
        """
        Test a dict value for equality.
        >>> Var('f1') == 42
        :param rhs: The value to compare against
        """
        return self._build_predicate(
            lambda value: eq(value, rhs),
            (Operation.EQ, tuple(self.path), freeze(rhs))
        )

    def __ne__(self, rhs):
        """
        Test a dict value for inequality.
        >>> Var('f1') != 42
        :param rhs: The value to compare against
        """
        return self._build_predicate(
            lambda value: value != rhs,
            (Operation.NE, tuple(self.path), freeze(rhs))
        )

    def __lt__(self, rhs):
        """
        Test a dict value for being lower than another value.
        >>> Var('f1') < 42
        :param rhs: The value to compare against
        """
        return self._build_predicate(
            lambda value: value < rhs,
            (Operation.LT, tuple(self.path), rhs)
        )

    def __le__(self, rhs):
        """
        Test a dict value for being lower than or equal to another value.
        >>> where('f1') <= 42
        :param rhs: The value to compare against
        """
        return self._build_predicate(
            lambda value: value <= rhs,
            (Operation.LE, tuple(self.path), rhs)
        )

    def __gt__(self, rhs):
        """
        Test a dict value for being greater than another value.
        >>> Var('f1') > 42
        :param rhs: The value to compare against
        """
        return self._build_predicate(
            lambda value: value > rhs,
            (Operation.GT, tuple(self.path), rhs)
        )

    def __ge__(self, rhs):
        """
        Test a dict value for being greater than or equal to another value.
        >>> Var('f1') >= 42
        :param rhs: The value to compare against
        """
        return self._build_predicate(
            lambda value: value >= rhs,
            (Operation.GE, tuple(self.path), rhs)
        )

    def exists(self):
        """
        Test for a dict where a provided key exists.
        >>> Var('f1').exists() >= 42
        :param rhs: The value to compare against
        """
        return self._build_predicate(
            lambda _: True,
            (Operation.EXISTS, tuple(self.path))
        )

    def matches(self, regex):
        """
        Run a regex test against a dict value (whole string has to match).
        >>> Var('f1').matches(r'^\w+$')
        :param regex: The regular expression to use for matching
        """
        return self._build_predicate(
            lambda value: re.match(regex, value),
            (Operation.MATCHES, tuple(self.path), regex)
        )

    def search(self, regex):
        """
        Run a regex test against a dict value (only substring string has to
        match).
        >>> Var('f1').search(r'^\w+$')
        :param regex: The regular expression to use for matching
        """
        return self._build_predicate(
            lambda value: re.search(regex, value),
            (Operation.SEARCH, tuple(self.path), regex)
        )

    def test(self, func, *args, **kwargs):
        """
        Run a user-defined test function against a dict value.
        >>> def test_func(val):
        ...     return val == 42
        ...
        >>> Var('f1').test(test_func)
        :param func: The function to call, passing the dict as the first
            argument
        :param *args: :param **kwargs: Additional arguments to pass
            to the test function
        """
        return self._build_predicate(
            lambda value: func(value, *args, **kwargs),
            (Operation.TEST, tuple(self.path), func, args)
        )

    def any(self, cond):
        """
        Checks if a condition is met by any element in a list,
        where a condition can also be a sequence (e.g. list).
        >>> Var('f1').any(Var('f2') == 1)
        Matches::
            {'f1': [{'f2': 1}, {'f2': 0}]}
        >>> Var('f1').any([1, 2, 3])
        # Match f1 that contains any element from [1, 2, 3]
        Matches::
            {'f1': [1, 2]}
            {'f1': [3, 4, 5]}
        :param cond: Either a Var that at least one element has to match or
                     a list of which at least one element has to be contained
                     in the tested element.
-        """
        if callable(cond):
            def _cmp(value):
                return is_iterable(value) and any(cond(e) for e in value)

        else:
            def _cmp(value):
                return is_iterable(value) and any(e in cond for e in value)

        return self._build_predicate(
            lambda value: _cmp(value),
            (Operation.ANY, tuple(self.path), freeze(cond))
        )

    def all(self, cond):
        """
        Checks if a condition is met by any element in a list,
        where a condition can also be a sequence (e.g. list).
        >>> Var('f1').all(Var('f2') == 1)
        Matches::
            {'f1': [{'f2': 1}, {'f2': 1}]}
        >>> Var('f1').all([1, 2, 3])
        # Match f1 that contains any element from [1, 2, 3]
        Matches::
            {'f1': [1, 2, 3, 4, 5]}
        :param cond: Either a Var that all elements have to match or a list
                     which has to be contained in the tested element.
        """
        if callable(cond):
            def _cmp(value):
                return is_iterable(value) and all(cond(e) for e in value)

        else:
            def _cmp(value):
                return is_iterable(value) and all(e in value for e in cond)

        return self._build_predicate(
            lambda value: _cmp(value),
            (Operation.ALL, tuple(self.path), freeze(cond))
        )


def where(key):
    """Ad hoc Var constructor."""
    key = key.split('.')
    return Var(key)
