Inspirations:
* Clean design patterns of application by Rober "Uncle Bob" Martin ([Architecture the Lost Years](http://www.youtube.com/watch?v=WpkDN78P884))
* Domain Driven Development by Martin Fowler & Eric Evans
* validation as boundary interfaces: [marshmallow](https://marshmallow.readthedocs.io/en/3.0/) or [cerberus](http://docs.python-cerberus.org/en/stable/)

Spheres of consideration:
* Clean design and ease of lightweight testing the key fragments of code on the first place.
* Time/space cost optimization taken as the second matter.

Tiers of Dharma:
* Data-level logic: traits & natures, formulae.
* Domain-specific logic: entities, aggregates, value objects, shared entities (between bounded contexts), policies, factories, domain services, repositories.
* Application-specific logic: application services, gateways, CQRS stacks, sagas. Task-, event- and data-driven applications, commands.
