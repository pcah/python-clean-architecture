class TraitError(Exception):
    pass


class TraitValidationError(TraitError):
    def __init__(self, errors, trait=None, *args, **kwargs):
        super(TraitValidationError, self).__init__(*args, **kwargs)
        self.errors = errors
        self.trait = trait

    def __str__(self):
        return "{result}; trait: {trait}; errors: {errors}".format(
            result=super(TraitValidationError, self).__repr__(),
            trait=self.trait or 'None',
            errors=self.errors or 'None')


class TraitInstantiationError(TraitError):
    pass
