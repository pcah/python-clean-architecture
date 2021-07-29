### python-clean-architecture

## Dependency Injection micro-framework

This package contains a micro-framework that serves as an implementation of [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection) pattern for the rest of [python-clean-architecture](https://github.com/pcah/python-clean-architecture) library. It is composed of:

- A [`Container`](container.py) as a central repository of DI definitions and their constructors. The Container isn't expected to be either singleton, global nor static. On the other side, every dependant has to have the Container supplied either by a helper function or by the injection process.
- A [`create_component` helper](component.py), which allows ad-hoc creation of an instance of a dependency, according to its DI context.
- A [`Component` mixin class or a `ComponentMeta` metaclass](component.py) designed to supply a class with capabilities of self-inspection of its DI context.
- An [`Inject` descriptor](descriptors.py) that knows how to get a dependency instance when it's needed. Alternatively, it marks an argument of a function as a place to inject the dependency instance.
- An [`inject` functional decorator](decorators.py) that injects values for all arguments marked with the `Inject` descriptor. It is a way to supply dependencies via function-wide scope instead of object-wide scope.
- A [`scope` decorator and `Scope` enumerable](container.py), which describe how often an instance should be created.

This library has potential to be extracted as an independent library in an undefined future when its API reaches stability.
