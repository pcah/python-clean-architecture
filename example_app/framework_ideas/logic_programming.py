
class PredicateDescriptor:
    def __init__(self, predicate):
        self.predicate = predicate

    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name

    def __get__(self, instance, owner):
        return self.predicate(instance)
