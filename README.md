# python-clean-architecture
[![GitHub version](https://badge.fury.io/gh/pcah%2Fpython-clean-architecture.svg)](https://badge.fury.io/gh/pcah%2Fpython-clean-architecture)
[![development status](https://img.shields.io/badge/development%20status-pre--alpha-orange.svg)](https://pypi.org/project/python-clean-architecture/)
[![Build Status](https://travis-ci.org/pcah/python-clean-architecture.svg?branch=master)](https://travis-ci.org/pcah/python-clean-architecture) 
[![codecov](https://codecov.io/gh/pcah/python-clean-architecture/branch/master/graph/badge.svg)](https://codecov.io/gh/pcah/python-clean-architecture) [![Join the chat at https://gitter.im/pcah/python-clean-architecture](https://badges.gitter.im/pcah/python-clean-architecture.svg)](https://gitter.im/pcah/python-clean-architecture?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

*python-clean-architecture* is a Python library aiming to equip you with a set of patterns to come closer to The Clean Architecture and a toolbox of adapters for integration with popular frameworks. Using them can make your code more focused on the knowledge you are trying to embody with your application and separation from technical details. A nice side-effects of this approach is an ease of plugging your application to a different variants of your infrastructure and lightweight testing the key fragments of your codebase.

#### Development Status

The library is still in a planning phase, so expect much refactorization and many changes to its API (Stage 2 - Pre-Alpha Status).

#### Inspirations

* Clean design patterns of application by Robert "Uncle Bob" Martin ([Architecture the Lost Years](http://www.youtube.com/watch?v=WpkDN78P884))
* Domain Driven Development by [Eric Evans](http://dddcommunity.org/book/evans_2003/) & [Martin Fowler](https://martinfowler.com/books/eaa.html)

#### Tiers of the architecture

* Data-level logic: data description objects, schemas, serialization, predicates, formulae.
* Domain-specific logic: bounded contexts (aka domains), entities, value objects, aggregates, repositories, policies, factories, domain services.
* Application-specific logic: use-cases, application services, gateways, CQRS stacks, sagas. Task-, event- and data-driven applications, commands.

#### Integrations:

One of the main goal of this library is to provide integration with adequate integrations: 

  * [TinyDb](https://tinydb.readthedocs.io) as DAO
  * more to come soon...