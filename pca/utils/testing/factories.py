# -*- coding: utf-8 -*-
from pca.data import Nature, Trait
from pca.exceptions import TraitInstantiationError


def nature_class_factory(args=None, kwargs=None, trait_name=None,
                         nature_name=None):
    """Builds a nature class with a single trait of specified type and name."""
    # construct the trait
    args = args or ()
    kwargs = kwargs or {}
    try:
        trait = Trait(*args, **kwargs)
    except TypeError as e:
        new_e = TraitInstantiationError(
            "Trait class got bad arguments: " + str(e))
        new_e.related_error = e
        raise new_e
    # construct the class
    nature_name = nature_name or 'DynamicallyBuiltEntity'
    trait_name = trait_name or 'trait'
    nature_class = type(nature_name, (Nature,), {trait_name: trait})

    return nature_class


def nature_object_factory(trait_class=None, args=None, kwargs=None,
                          trait_name=None, nature_name=None):
    """Builds an nature with a single trait of specified type and name."""
    nature_class = nature_class_factory(
        trait_class, args, kwargs, trait_name, nature_name)
    return nature_class()


def build_datasets(data):
    """
    A generator of (nature, value) tuples that are prepared as datasets for
    tests.

    Input data are expected to be in the form of:
    {
        (Int, (42,), frozendict(cast=False)): [1, 1.0, 1L],
        (Float, (), frozendict(cast=True)): [1, 1.0, 1L],
        String: ['plain string', u'dąmn uńićodę'],
    }
    where keys are interpreted as an inpout to simple_simple_nature_factory
    and values are lists of test values.
    """
    for params, values in data.items():
        for value in values:
            params = params if isinstance(params, (list, tuple)) else (params,)
            nature = nature_object_factory(*params)
            yield (nature, value)
