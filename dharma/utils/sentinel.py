class Sentinel(object):
    """
    Sentinel class for constants with useful reprs.
    Based on sentinel class from traits package from IPython team.
    """
    def __init__(self, name, module, docstring=None):
        self.name = name
        self.module = module
        if docstring:
            self.__doc__ = docstring

    def __repr__(self):
        return '{module}.{name}'.format(module=self.module, name=self.name)
