### python-clean-architecture
## Example application

This package contains a full-featured, tested and runnable web application, as a showcase of the [`python-clean-architecture`](https://github.com/pcah/python-clean-architecture). The core domain of the application is the process of organizing group meetings, based on the [Meetup.com](https://www.meetup.com/) system.

For more functional description, go to the [DESCRIPTION doc](docs/DESCRIPTION.md). 

This package has the potential to be extracted as an independent repository in an undefined future when its codebase reaches stability.

### 1. Origin
It is a reimplementation of [Modular Monolith with DDD](https://github.com/kgrzybek/modular-monolith-with-ddd) Project in Python language (the original is written in C# using ASP.NET Core MVC). All kudos for some great design go to © [Kamil Grzybek](https://www.kamilgrzybek.com/), the author of the original repository.

### 2. The Purpose & the Reason

As described by the [original project](https://github.com/kgrzybek/modular-monolith-with-ddd):

### 2.1. The Purpose of this Repository

> This is a list of the main goals of this repository:
> 
> - Showing how you can implement a **monolith** application in a **modular** way
> - Presentation of the **full implementation** of an application
>   - This is not another simple application
>   - This is not another proof of concept (PoC)
>   - The goal is to present the implementation of an application that would be ready to run in production
> - Showing the application of **best practices** and **object-oriented programming principles**
> - Presentation of the use of **design patterns**. When, how and why they can be used
> - Presentation of some **architectural** considerations, decisions, approaches
> - Presentation of the implementation using **Domain-Driven Design** approach (**tactical** patterns)
> - Presentation of the implementation of **Unit Tests** for Domain Model (Testable Design in mind)
> 
> — Kamil Grzybek (2020), [Modular Monolith with DDD](https://github.com/kgrzybek/modular-monolith-with-ddd) 


### 2.2. The Reason

> The reason for creating this repository is the lack of something similar. Most sample applications on GitHub have at least one of the following issues:
> - Very, very simple - few entities and use cases implemented
> - Not finished (for example there is no authentication, logging, etc..)
> - Poorly designed (in my opinion)
> - Poorly implemented (in my opinion)
> - Not well described
> - Assumptions and decisions are not clearly explained
> - Implements "Orders" domain - yes, everyone knows this domain, but something different is needed
> - Implemented in old technology
> - Not maintained
>
> — Kamil Grzybek (2020), [Modular Monolith with DDD](https://github.com/kgrzybek/modular-monolith-with-ddd) 
