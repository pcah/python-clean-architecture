class TraitError(Exception):
    pass


class TraitValidationError(TraitError):
    pass


class TraitInstantiationError(TraitError):
    pass
