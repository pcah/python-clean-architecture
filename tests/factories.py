# encoding: utf-8
from dharma import Entity
from dharma.exceptions import TraitInstantiationError


def simple_entity_factory(trait_class, args=None, kwargs=None, trait_name=None,
                          entity_name=None, force_instantiate=False):
    "Builds an entity with a single trait of specified type and name."
    # construct the trait
    trait_name = trait_name or 'trait'
    if args or kwargs or force_instantiate:
        args = args or ()
        kwargs = kwargs or {}
        try:
            trait = trait_class(*args, **kwargs)
        except TypeError as e:
            new_e = TraitInstantiationError("Trait class got bad arguments")
            new_e.related_error = e
            raise new_e
    else:
        trait = trait_class
    # construct the class
    entity_name = entity_name or 'DynamicallyBuiltEntity'
    entity_class = type(entity_name, (Entity,), {trait_name: trait})
    entity_object = entity_class()

    return entity_object


def build_datasets(data):
    """
    Returns list of (entity, value) tuples that are prepared as datasets for
    tests.

    Input data are expected to be in the form of:
    {
        (Int, (42,), frozendict(cast=False)): [1, 1.0, 1L],
        (Float, (), frozendict(cast=True)): [1, 1.0, 1L],
        String: ['plain string', u'dąmn unicode'],
    }
    where keys are interpreted as TraitDefinition and values are lists of
    test values.
    """
    datasets = []
    for params, values in data.items():
        for value in values:
            params = params if isinstance(params, (list, tuple)) else (params,)
            entity = simple_entity_factory(*params)
            datasets.append((entity, value))
    return datasets
