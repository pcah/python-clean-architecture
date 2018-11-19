# python-clean-architecture
[![GitHub version](https://badge.fury.io/gh/pcah%2Fpython-clean-architecture.svg)](https://badge.fury.io/gh/pcah%2Fpython-clean-architecture) [![Build Status](https://travis-ci.org/pcah/python-clean-architecture.svg?branch=master)](https://travis-ci.org/pcah/python-clean-architecture) [![Coverage Status](https://coveralls.io/repos/github/pcah/python-clean-architecture/badge.svg?branch=master)](https://coveralls.io/github/pcah/python-clean-architecture?branch=master) [![Join the chat at https://gitter.im/pcah/python-clean-architecture](https://badges.gitter.im/pcah/python-clean-architecture.svg)](https://gitter.im/pcah/python-clean-architecture?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

*python-clean-architecture* is a toolkit library aiming to equip you with a set of patterns and some implementations of The Clean Architecture. Using them can make your code focused on the knowledge you are trying to embody. A nice side-effect of this process is an ease of lightweight testing the key fragments of your codebase.

#### Development Status

The library is still in a planning phase, so expect multiple refactorizations and many changes to its API (Stage 2 - Pre-Alpha Status).

#### Inspirations

* Clean design patterns of application by Robert "Uncle Bob" Martin ([Architecture the Lost Years](http://www.youtube.com/watch?v=WpkDN78P884))
* Domain Driven Development by [Eric Evans](http://dddcommunity.org/book/evans_2003/) & [Martin Fowler](https://martinfowler.com/books/eaa.html)

#### Tiers of the architecture

* Data-level logic: data description objects, schemas, serialization, predicates, formulae.
* Domain-specific logic: bounded contexts (aka domains), entities, value objects, aggregates, repositories, policies, factories, domain services.
* Application-specific logic: use-cases, application services, gateways, CQRS stacks, sagas. Task-, event- and data-driven applications, commands.
