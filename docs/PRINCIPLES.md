### python-clean-architecture

## The Principles

#### 1. Domain *First* Design

The library promotes thinking that your domain should be *the first thing* you start to develop on the first day of your project. No choice of a framework should be required -- you may not discover yet enough information needed to choose one. Similarly, neither infrastructure configuration nor developer toolset should be required. You should be able to start by describing your domain with pseudocode.

Quotes:
> For most software projects, the primary focus should be on the domain and domain logic.
>
> — Eric Evans (2003), [Domain Driven Design: Tackling Complexity in the Heart of Software](http://dddcommunity.org/book/evans_2003/)

> A good software architecture allows decisions about frameworks, databases, web-servers, and other environmental issues and tools, to be deferred and delayed. A good architecture makes it unnecessary to decide on Rails, or Spring, or Hibernate, or Tomcat or MySql, until much later in the project.
>
> — Robert Martin (2011), [Clean Coder Blog: Screaming Architecture](https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html)

#### 2. Keep it simple and straightforward

The library should encourage the developer to follow [KISS](https://en.wikipedia.org/wiki/KISS_principle) principle. There are several ways to expand this abbreviation and we prefer to state it as is mentioned above: *keep things simple and straightforward*. *Simple* means to us both *without unnecessary complication* and *complexity*. *Straightforward* means *stating its intent explicitly*.

Both terms describe either application component as a single element and relations between components. It is easy to build fancy features with lots of objects and relations and thus make the design complicated. It is hard to keep things minimalist and yet expressible. There are several ways you can embody this idea and we mention three of these below:

##### a) Pure Functions

Pure functions are side-effect-free functions, which returned value is based only on its input. This is especially important when mentioned functions implement valid transformations between states of the application. For example, a function may describe how a value object representing money transforms into a (new) value object of another currency. We advise you not to expect such function to implicitly retrieve exchange ratio from an external source. Let the function that makes the transformation take the exchange ratio as an argument.

> *Side-effect-free Functions.* Place as much of the logic of the program as possible into functions, operations that return results with no observable side effects. Strictly segregate commands (methods which result in modifications to observable state) into very simple operations that do not return domain information. Further control side effects by moving complex logic into value objects when a concept fitting the responsibility presents itself. All operations of a value object should be side-effect­‐free functions.
>
> — Eric Evans (2015), [Domain-­Driven Design Reference](http://domainlanguage.com/ddd/reference/)

##### b) Self-contained Classes

Self-contained class has its intent formulated and understandable by its code and its code only. This means that you don't need to gather bits of code placed outside of the class to understand its purpose.

> *Standalone Classes.* Even within a module, the difficulty of interpreting a design increases wildly as dependencies are added. This adds to mental overload, limiting the design complexity a developer can handle. Implicit concepts contribute to this load even more than explicit references.
Low coupling is fundamental to object design. When you can, go all the way. Eliminate all other concepts from the picture. Then the class will be completely self­‐contained and can be studied and understood alone. Every such self­‐contained class significantly eases the burden of understanding a module.
>
> — Eric Evans (2015), [Domain-­Driven Design Reference](http://domainlanguage.com/ddd/reference/)

##### c) Single Responsibility Principle

[The Single Responsibility Principle](https://web.archive.org/web/20150905081024/http://www.objectmentor.com/resources/articles/srp.pdf) promotes that a component should be responsible for one single thing only.

Let's take a look at one practical example. The core of an application should be expressible with objects as simple as possible (compare to the concept of "[Plain Old Java Objects](https://en.wikipedia.org/wiki/Plain_old_Java_object)"). Entities should not be entangled with neither the persistence framework nor validation schemes. The same goes for all the business logic objects, like value objects, services and events. They should be focused on expressing both: fragments of the business logic and intentions of the specific component design. The validation and the database mapping should be expressed with other components, stating their intent by explicit separation.

This observation makes frameworks like SQLAlchemy or Django deemed providing inappropriate or unsuitable design. Take a look at Django's `ModelForm`. Its design puts three different responsibilities into one class: (1) HTML rendering, (2) input data validation & (3) integration with data schema declaration class (a `Model` class). For the purpose of letting a developer to reimplement one of responsibilities, you should make them separated into three classes. You can decide the degree and the direction of coupling, but keeping responsibilities apart will bring you closer to The Clean Architecture. If you don't want to bring superfluous code to your project, use configurable constructor helpers, which give the developer freedom to use them for auto-generation of code or build components by hand.

#### 3. Layered architecture

One of the main purposes The Clean Architecture exists is separation of concerns with regard to the business logic. Layers, represented by circles in [the classic diagrams of _onion_ architectures](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html), represent code components the more logic-pure, the closer to the center. In the very center lie framework- and application-independent code that models the knowledge about the domain itself. The key feature of this separation is _The Dependency Rule_ quoted below and the following corollary: every technical detail should be resolved as far outside of the domain layer as possible and reasonable.

Inspired by Robert Martin's The Clean Architecture, this library formulates three key layers: domain, application and framework (with the latter represented by the `integrations` package). The drivers & connections layer (implicit to the library) hides beneath the framework layer.

Quotes:
> The reason that good architectures are centered around use-cases is so that architects can safely describe the structures that support those use-cases without committing to frameworks, tools, and environment.
>
> — Robert Martin (2011), [Screaming Architecture](https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html)

> The overriding rule that makes this architecture work is _The Dependency Rule_. This rule says that source code dependencies can only point inwards. Nothing in an inner circle can know anything at all about something in an outer circle.
>
> — Robert Martin (2012), [The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

#### 4. Coupling management

The library wants to promote a design that makes its components coupled only there when it is needed and suitable. On the other hand, components that have reason to exists only together or don't exist at all, should be tightly coupled.

[Loose coupling](https://en.m.wikipedia.org/wiki/Loose_coupling) is a design technique of deferring architecture decisions (vide **#&#x2060;1**) and improving code reusability. It also is a way to achieve separation of layers (vide **#&#x2060;3**). To provide loose coupling, this library uses [dependency injection](https://en.wikipedia.org/wiki/Dependency_injection). We decided to use [our own implementation](https://github.com/pcah/python-clean-architecture/blob/master/pca/utils/dependency_injection.py) that focuses on being stateful and non-global. Our DI container is a [non-global Singleton by single instance](https://softwareengineering.stackexchange.com/a/40610) and an explicit (and commonly the only one) argument of a component's constructor.

Most of the time, dependency injection is achieved using interfaces (in a python meaning): abstract classes that define its API as [contracts](https://en.wikipedia.org/wiki/Design_by_contract) between the components. We also use the interfaces along with Python 3's [type](https://www.python.org/dev/peps/pep-0484/) [annotations](https://www.python.org/dev/peps/pep-0526/). This approach synergize with static analysis features of IDEs or language linters.

Quotes:

> There are several ways to describe coupling, but it boils down to this: If changing one module in a program requires changing another module, then coupling exists. (...) Coupling also occurs when code in one module uses code from another, perhaps by calling a function or accessing some data. At this point, it becomes clear that, unlike duplication, you can’t treat coupling as something to always avoid. You can break a program into modules, but these modules will need to communicate in some way — otherwise, you’d just have multiple programs. Coupling is desirable, because if you ban coupling between modules, you have to put everything in one big module. Then, there would be lots of coupling — just all hidden under the rug. So coupling is something we need to control, but how?
>
> — Martin Fowler (2001), [Reducing Coupling](https://www.martinfowler.com/ieeeSoftware/coupling.pdf)

> Loose coupling enables independent variability among the participants, allowing for example one component to change its implementation technology or its version without affecting other systems. In an enterprise-wide or inter-enterprise (i.e., B2B) integration scenario, independent variability has considerable value because one party usually doesn't have control over all applications, meaning that some components can change without central coordination or approval. For example, if a business partner decides to upgrade to the latest version of SAP there is little one can do to stop them. In the reverse scenario, your business might need to update components without being able to force the other side to make the corresponding change.
Loose coupling is like buying insurance. It's best when you don't need it, but that doesn't mean you wasted your money.
>
> — Gregor Hohpe, Bobby Woolf (2003), [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/index.html)

#### 5. Be open to reimplementation

The library's components should be open to reimplementation of other components. This is somewhat an aspect of self-contained classes that support SRP (vide **#&#x2060;2**), but may necessitate some extra effort to introduce loose coupling (vide **#&#x2060;4**) where it is needed.

Layered architecture (vide **#&#x2060;3**) using dependency injection keeps things easy to detach and reimplement, especially on the edge of two layers. But we don't want to stop at this level and we aim to keep things exchangeable with different implementations. For example, if a component within some layer can be implemented in a few different ways, other objects of mentioned layer should not depend on any concrete implementation. They should define a common contract with its interface class and keep their expectations within boundaries of that contract. The library don't have to provide all possible implementations, but it shouldn't keep you from writing your own.

At the end, the library should become something more similar to a toolbox, that let's you choose tools as you need them, than a framework that forces you to do specific things. Feel free to use only a part of the implementations given by the library or reimplement them with your own code along with the growth of your application.

Quotes:

> *Pluggable Component Framework.* Distill an abstract core of interfaces and interactions and create a framework that allows diverse implementations of those interfaces to be freely substituted. Likewise, allow any application to use those components, so long as it operates strictly through the interfaces of the abstract core.
>
> — Eric Evans (2015), [Domain-­Driven Design Reference](http://domainlanguage.com/ddd/reference/)

#### 6. Batteries included

The library aims to provide integrations with popular libraries, frameworks and their design patterns. Much of the effort put into designing a clean architecture library would have been futile without proper integrations with The Real World of programming in Python. This real world is day-to-day struggle you, The Developer, take to develop and maintain your application, library or whatever you do. PCA strives to support you with a set of useful integrations. Of course it can (and should) never provide all possible integrations and their number will always be too small, but our goal is to provide at least the key ones. Thanks to The Principle **#&#x2060;5**, we try to provide clean separation and reliable means to reimplement the integrations in a way you need, if there is no implementation you need.
