# python-clean-architecture
![GitHub tag](https://img.shields.io/github/tag-date/pcah/python-clean-architecture.svg?style=popout)
[![development status](https://img.shields.io/badge/development%20status-pre--alpha-orange.svg)](https://pypi.org/project/python-clean-architecture/)
[![Build Status](https://travis-ci.org/pcah/python-clean-architecture.svg?branch=master)](https://travis-ci.org/pcah/python-clean-architecture)
[![codecov](https://codecov.io/gh/pcah/python-clean-architecture/branch/master/graph/badge.svg)](https://codecov.io/gh/pcah/python-clean-architecture) [![Join the chat at https://gitter.im/pcah/python-clean-architecture](https://badges.gitter.im/pcah/python-clean-architecture.svg)](https://gitter.im/pcah/python-clean-architecture?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

*python-clean-architecture* is a Python library aiming to bring your code closer to The Clean Architecture. The first goal is to equip you with a set of patterns and good practices. The second one is to provide you a toolbox of adapters for integration with popular frameworks. Using them can make your code more focused on the knowledge you are trying to embody with your application and separation from technical details. A nice side-effects of this approach is an ease of plugging your application to a different variants of your infrastructure and lightweight testing the key fragments of your codebase.

#### Development Status  (Stage 2 - Pre-Alpha Status)

**THE LIBRARY IS NOT PRODUCTION- OR DEVELOPMENT-READY**. If you want to make it useful, come and help. See [CONTRIBUTING](CONTRIBUTING.md) for details.

The concept for this library is ambitious and its core team has not as much spare time as it would like to dedicate, so don't expect rapid development here. If you are interested in making its progress more apparent, you are more than welcomed to propose your help. The core team reserves the right to choose focus points and scopes for the library, however.

The library is still in a planning phase, so expect much refactorization and many changes to its API.

#### Motivation & inspirations

There is a saying that every developer should write his own framework once in a lifetime. Being happily married with our professional jobs, we do this library in our spare time. Why? To show ourselves and fellow developers there is an achievable way to come closer to The Clean Architecture using a finite amount of effort. We try to show that Python community can build well designed applications as well. We treat following lectures as food for thoughts as we strive to implement ideas found there:

- _Clean architecture_ by [Robert "Uncle Bob" Martin](https://www.oreilly.com/library/view/clean-architecture-a/9780134494272/) (2017) (or e.g. [Architecture the Lost Years](http://www.youtube.com/watch?v=WpkDN78P884) (2011))
- _Onion Architecture_ by [Jeffrey Palermo](http://jeffreypalermo.com/blog/the-onion-architecture-part-1/) (2008)
- _Hexagonal Architecture_ by [Alistair Cockburn](http://alistair.cockburn.us/Hexagonal+architecture) (2005)
- _Domain-Driven Design_ by [Eric Evans](http://dddcommunity.org/book/evans_2003/) (2003) & [Martin Fowler](https://martinfowler.com/tags/domain%20driven%20design.html) (2002)


#### The Principles of the Library

Here you can find a short version of The Principles the library is meant to follow. [If you want to read more about them, take a look at our docs](docs/PRINCIPLES.md).

1. **Domain First Design.** Building an application should begin with its business intent and without any decision about a framework or other technical details.
2. **Keep it simple and straightforward.** There's a great value of having simple business objects, like dataclasses. Decompose your every component to make them correspond a specific single responsibility, but only as far as to be straightforward in your intents. Keep your state-transformation functions pure and classes self-contained.
3. **Layered architecture.** Keep domain & application logic pure. Separate them in layers, the same goes for technical details for a framework & the whole system/hardware environment. Dependencies between layers should point only inwards, with domain in the core. You can have more layers if you feel a need, but keep in mind that every layer is a cost to maintain.
4. **Coupling management.** Quite often components don't need to be tightly connected and have knowledge of construction methods of the other one. Use Dependency Injection technique then, along with interfaces that define other component's contract. Dependency Injection may also help to control lifecycle of components.
5. **Be open to reimplementation.** If a component may be implemented in several different manners, keep its design open to be reimplemented in different ways. Use interfaces that define contracts with other components. Use coupling management using these interfaces to interact with other components.
6. **Batteries included.** The library should provide integrations with the key Python projects.

#### Tiers of the architecture

* Data-level logic: data description objects, factories, serialization, predicates, formulae. [Its not a specific layer]
* Domain layer: bounded contexts (aka domains), entities, value objects, aggregates, repositories, policies, factories, domain services.
* Application-specific logic: use-cases, application services, gateways, CQRS stacks, sagas. Task-, event- and data-driven applications, commands.

#### Micro-frameworks

To accomplish the goals in a most convenient and readable manner, the library introduces some helper micro-frameworks:

  * [pca/utils/dependency_injection](pca/utils/dependency_injection) to provide loose coupling between components in the pythonic way: interface-based with type annotations, declarative dependencies, introspection, no necessity for global-state container.
  * [utils/errors.py](pca/utils/errors.py) as a declarative way to provide l10n-independent errors with params & hints for developers, together with thematic catalogues of errors.

#### Integrations

One of the goals of this library is to provide integration with popular Python frameworks and libraries. Here are the most notable ones:

  * [TinyDb](https://tinydb.readthedocs.io) as a [DAO](pca/integration/tinydb.py)
  * YAML, JSON or INI file loaded into the memory as a [DAO](pca/data/dao/file.py)
  * more to come soon...
