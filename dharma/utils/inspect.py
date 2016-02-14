# -*- coding: utf-8 -*-


def get_all_subclasses(cls):
    for subclass in cls.__subclasses__():
        for cls in get_all_subclasses(subclass):
            yield cls
        yield subclass


def is_argspec_valid(function, arg_number=None, kwargs_names=None):
    """
    Args:
        function - function to be checked.
        arg_number - number of all arguments (named or not) which is going to
            be used calling the function.
        kwargs_names - iterable of names for keyword arguments whose existence
            in signature is going to be verified.

    Returns:
        bool - True iff function is valid to be valid with specified arg
            number and keyword arguments names.
    """
    # TODO if six.PY3 use SignatureObject
    # else:
    # import inspect
    # (len(inspect.getargspec(listener).args) == 3 or
    #  inspect.getargspec(listener).varargs is not None)
    return True
