def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

class GenericAnnotation(object):
    def __getattr__(self, name):
        """ Returns a dumb function """
        print 'a'
        return 1
        return lambda x: x
