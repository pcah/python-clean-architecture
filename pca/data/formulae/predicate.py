"""
Contains the querying interface.
Starting with :class:`Var` you can construct complex
queries:
>>> ((where('f1') == 5) & (where('f2') != 2)) | where('s').matches(r'^\w+$')
(('f1' == 5) and ('f2' != 2)) or ('s' ~= ^\w+$ )
Predicates are executed by using the ``__call__``:
>>> from pca.data.formulae import Predicate, where
>>> predicate = where('val') == 5  # type: Predicate
>>> predicate({'val': 5})
True
>>> predicate({'val': 1})
False
"""
from enum import Enum
import re
from typing import (  # flake8: noqa
    Any,
    Callable,
    Iterable,
    Optional,
    Tuple,
    Union,
)

from pca.utils.collections import freeze, is_iterable
from pca.utils.operators import eq, resolve_path, check_path


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


COMPOSITE_PREDICATE = (
    Operation.OR,
    Operation.AND,
    Operation.NOT
)


class Predicate(object):
    """
    Enwraps the actual condition function, which is run when the
    predicate is evaluated by calling its object. Predicates can be combined
    with logical and/or and modified with logical not.
    """
    def __init__(self, test, operator, args, var_name=None):
        self.test = test
        self.args = args
        self.operator = operator
        self._composite = self.operator in COMPOSITE_PREDICATE
        self.var_name = var_name

    def __call__(self, value):
        return self.test(value)

    def __hash__(self):
        return hash((self.operator, self.args, self.var_name))

    def __repr__(self):
        return 'Predicate({}{}, {})'.format(
            self.var_name + ', ' if self.var_name else '',
            self.operator.name,
            self.args
        )

    def __eq__(self, other):
        if not isinstance(other, Predicate):
            return False
        return self.operator, self.args, self.var_name == \
            other.operator, other.args, other.var_name

    # --- Associativity of Predicates

    def __and__(self, other):
        # We use a frozenset for the definitions as the AND operation
        # is commutative: (a | b == b | a)
        return Predicate(
            test=lambda value: self(value) and other(value),
            operator=Operation.AND,
            args=frozenset([self, other])
        )

    def __or__(self, other):
        # We use a frozenset for the definitions as the OR operation
        # is commutative: (a & b == b & a)
        return Predicate(
            test=lambda value: self(value) or other(value),
            operator=Operation.OR,
            args=frozenset([self, other])
        )

    def __invert__(self):
        return Predicate(
            test=lambda value: not self(value),
            operator=Operation.NOT,
            args=(self,)
        )


class Var(object):
    # noinspection PyUnresolvedReferences
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
    >>> find(where('name') == True)

    Note that:
    * ``where(...)`` is a shorthand for ``Var()[...]``, ie. creates
    an anonymous variable with specified query path.
    * ``var(foo.bar.name)`` is a shorthand for ``Var('name')['foo.bar.name']``
    ie. creates a variable with specified query path, named as the last part
    of the dotted Python path.

    Queries are executed by calling the Predicate object. They expect to get
    the element to test as the first argument and return ``True`` or ``False``
    depending on whether the elements matches the predicate or not.
    """

    def __init__(self, name=None, _path=None):
        # type: (str, Union[str, Iterable, None]) -> None
        """
        :param name: (optional) A name for the Var instance. Variables
         in a formula may be equated using their names.
        :param _path: (optional) A technical argument, used for passing
         path tuple between Var constructors.
        """
        self._name = name
        self._path = None  # type: Tuple[Optional[str]]
        if _path is None:
            self._path = ()  # type: ignore noqa
        elif is_iterable(_path):
            self._path = tuple(_path)  # type: ignore noqa
        else:
            self._path = (_path,)  # type: ignore noqa

    def __getattr__(self, item):
        # type: (str) -> Var
        """
        Returns new Var instance with the same name of variable but its path
        extended by additional path element, given with `item` argument.

        :param item: A path element.
        :return: A new Var instance with extended path.
        """
        return Var(self._name, self._path + (item,))

    def __getitem__(self, item):
        # type: (str) -> Var
        """
        Returns new Var instance with the same name of variable but its path
        extended by dotted path, given with `item` argument.

        :param item: A Python dotted path.
        :return: A new Var instance with extended path.
        """
        return Var(self._name, self._path + tuple(item.split('.')))

    def _build_predicate(self, test, operation, args):
        # type: (Callable[[Any, Any], Any], Operation, Iterable) -> Predicate
        """
        Generate a Predicate object based on a test function.

        :param test: The test the Predicate executes.
        :param operation: An `Operation` instance for the Predicate.
        :return: A `Predicate` object
        """
        if not self._path:
            raise ValueError('Var has no path')
        return Predicate(
            check_path(test, self._path),
            operation,
            args,
            self._name
        )

    def __eq__(self, rhs):
        # type: (Any) -> Predicate
        """
        Test the value for equality.
        >>> var('f1') == 42

        :param rhs: The value to compare against. It can either be a plain
         value or a Var instance which points to another field on the value
         that will be used during evaluation.
        :returns: A predicate of this comparison.
        """
        rhs_curried = _curry_rhs(rhs)
        return self._build_predicate(
            lambda lhs, value: eq(lhs, rhs_curried(value)),
            Operation.EQ,
            (self._path, freeze(rhs))
        )

    def __ne__(self, rhs):
        # type: (Any) -> Predicate
        """
        Test the value for inequality.
        >>> var('f1') != 42
        >>> var('f1') != var('f2')

        :param rhs: The value to compare against. It can either be a plain
         value or a Var instance which points to another field on the value
         that will be used during evaluations.
        :returns: A predicate of this comparison.
        """
        rhs_curried = _curry_rhs(rhs)
        return self._build_predicate(
            lambda lhs, value: lhs != rhs_curried(value),
            Operation.NE,
            (self._path, freeze(rhs))
        )

    def __lt__(self, rhs):
        # type: (Any) -> Predicate
        """
        Test the value for being lower than another value.
        >>> var('f1') < 42

        :param rhs: The value to compare against. It can either be a plain
         value or a Var instance which points to another field on the value
         that will be used during evaluations.
        :returns: A predicate of this comparison.
        """
        rhs_curried = _curry_rhs(rhs)
        return self._build_predicate(
            lambda lhs, value: lhs < rhs_curried(value),
            Operation.LT,
            (self._path, rhs)
        )

    def __le__(self, rhs):
        # type: (Any) -> Predicate
        """
        Test the value for being lower than or equal to another value.
        >>> where('f1') <= 42

        :param rhs: The value to compare against. It can either be a plain
         value or a Var instance which points to another field on the value
         that will be used during evaluations.
        :returns: A predicate of this comparison.
        """
        rhs_curried = _curry_rhs(rhs)
        return self._build_predicate(
            lambda lhs, value: lhs <= rhs_curried(value),
            Operation.LE,
            (self._path, rhs)
        )

    def __gt__(self, rhs):
        # type: (Any) -> Predicate
        """
        Test the value for being greater than another value.
        >>> var('f1') > 42

        :param rhs: The value to compare against. It can either be a plain
         value or a Var instance which points to another field on the value
         that will be used during evaluations.
        :returns: A predicate of this comparison.
        """
        rhs_curried = _curry_rhs(rhs)
        return self._build_predicate(
            lambda lhs, value: lhs > rhs_curried(value),
            Operation.GT,
            (self._path, rhs)
        )

    def __ge__(self, rhs):
        # type: (Any) -> Predicate
        """
        Test the value for being greater than or equal to another value.
        >>> var('f1') >= 42

        :param rhs: The value to compare against. It can either be a plain
         value or a Var instance which points to another field on the value
         that will be used during evaluations.
        :returns: A predicate of this comparison.
        """
        rhs_curried = _curry_rhs(rhs)
        return self._build_predicate(
            lambda lhs, value: lhs >= rhs_curried(value),
            Operation.GE,
            (self._path, rhs)
        )

    def exists(self):
        # type: () -> Predicate
        """
        Test for a dict/object where a provided key exists.
        >>> var('f1').exists()
        """
        return self._build_predicate(
            lambda _, __: True,
            Operation.EXISTS,
            (self._path,)
        )

    def matches(self, regex):
        # type: (str) -> Predicate
        """
        Run a regex test against a dict value (whole string has to match).
        >>> var('f1').matches(r'^\w+$')

        :param regex: The regular expression to use for matching
        """
        return self._build_predicate(
            lambda lhs, value: bool(re.match(regex, lhs)),
            Operation.MATCHES,
            (self._path, regex)
        )

    def search(self, regex):
        # type: (str) -> Predicate
        """
        Run a regex test against the value (only substring string has to
        match).
        >>> var('f1').search(r'^\w+$')

        :param regex: The regular expression to use for matching
        """
        return self._build_predicate(
            lambda lhs, value: bool(re.search(regex, lhs)),
            Operation.SEARCH,
            (self._path, regex)
        )

    def test(self, func, *args, **kwargs):
        # type: (Callable[..., bool], *Any, **Any) -> Predicate
        """
        Run a user-defined test function against the value.
        >>> def test_func(val):
        ...     return val == 42
        ...
        >>> var('f1').test(test_func)

        :param func: The function to call, passing the dict as the first
            argument
        :param args:
        :param kwargs:
            Additional arguments to pass to the test function
        """
        return self._build_predicate(
            lambda lhs, value: func(lhs, *args, **kwargs),
            Operation.TEST,
            (self._path, func, args, freeze(kwargs))
        )

    def any(self, cond):
        # type: (Union[Predicate, Iterable]) -> Predicate
        """
        Checks if a condition is met by any element in a list,
        where a condition can also be a sequence (e.g. list).
        >>> var('f1').any(var('f2').exists())
        Matches::
            {'f1': [{'f2': 1}, {'f2': 0}]}
        >>> var('f1').any([1, 2, 3])
        # Match f1 that contains any element from [1, 2, 3]
        Matches::
            {'f1': [1, 2]}
            {'f1': [3, 4, 5]}

        :param cond: Either a Predicate that at least one element has to match
         or a list of which at least one element has to be contained
         in the tested element.
-        """
        if callable(cond):
            def _cmp(value):
                return is_iterable(value) and any(cond(e) for e in value)

        else:
            def _cmp(value):
                return is_iterable(value) and any(e in cond for e in value)

        return self._build_predicate(
            lambda lhs, value: _cmp(lhs),
            Operation.ANY,
            (self._path, freeze(cond))
        )

    def all(self, cond):
        # type: (Union[Predicate, Iterable]) -> Predicate
        """
        Checks if a condition is met by any element in a list,
        where a condition can also be a sequence (e.g. list).
        >>> var('f1').all(var('f2').exists())
        Matches::
            {'f1': [{'f2': 1}, {'f2': 1}]}
        >>> var('f1').all([1, 2, 3])
        # Match f1 that contains any element from [1, 2, 3]
        Matches::
            {'f1': [1, 2, 3, 4, 5]}

        :param cond: Either a Predicate that all elements have to match or
         a list which has to be contained in the tested element.
        """
        if callable(cond):
            def _cmp(value):
                return is_iterable(value) and all(cond(e) for e in value)

        else:
            def _cmp(value):
                return is_iterable(value) and all(e in value for e in cond)

        return self._build_predicate(
            lambda lhs, value: _cmp(lhs),
            Operation.ALL,
            (self._path, freeze(cond))
        )


# noinspection PyProtectedMember
def _curry_rhs(rhs):
    # type: (Any) -> Callable[[Any], Any]
    """
    Late evaluation of a RHS of an operation.

    :param rhs: Right-hand side of an operation.
    :returns: If RHS is a Var instance, it will return a method for
     an extraction of a value when the value is evaluated. Otherwise, it
     returns a constant function of RHS.
    """
    if isinstance(rhs, Var):
        return resolve_path(rhs._path)
    return lambda value: rhs


def var(path):
    # type: (str) -> Var
    """
    Ad hoc Var constructor. The Var is named as the last element of the path.

    :param path: A Python dotted path.
    """
    name = path.rsplit('.', 1)[-1]
    return Var(name)[path]


def where(path):
    # type: (str) -> Var
    """
    Ad hoc anonymous Var constructor.

    :param path: A Python dotted path.
    """
    return Var()[path]
