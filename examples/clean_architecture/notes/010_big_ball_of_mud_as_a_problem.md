[[⬅ Back to ToC](../README.md)]

# 1. Big ball of mud as a problem

> _A Big Ball of Mud is a haphazardly structured, sprawling, sloppy, 
duct-tape-and-baling-wire, spaghetti-code jungle. These systems show 
unmistakable signs of unregulated growth, and repeated, expedient repair. 
Information is shared promiscuously among distant elements of the system, 
often to the point where nearly all the important information becomes global 
or duplicated._
> — Brian Foote and Joseph Yoder, _Big Ball of Mud_. Fourth Conference 
on Patterns Languages of Programs (PLoP '97/EuroPLoP '97) Monticello, 
Illinois, September 1997

### Stating the problem

The quote above sounds frightening and extreme. But we all witness it as 
we Look at following symptoms. If you experience a few of them, these articles 
are for you:
* The application is a spaghetti of close coupled classes without clear 
responsibilities. Every new developer has to have a long introductory period
before they can locate the piece of code they are searching for
unassisted.

* A large portion of codebase can be tested only with end-to-end tests,
because many of its components have hard to replicate intermediary states.

* Even seasoned programmers are afraid of developing some areas
of the application. Pieces of code, that you can find there, are fragile,
messy and hard to understand. _Here are lions_, as was written on the edges of 
medieval maps.

* The situation becomes worse and worse with every bug fix and every change
request your business demands, even when your co-developers put a lot of effort
to reduce the technical dept.

Do you know these symptoms? We have seen it too. Too many times.

### What's the reference point?

You could think that the problems we've stated are imminent to any software design.
So let's take a look now at this picture below. This is the basic idea of 
The Clean Architecture [[1]](#ref-1) by Uncle Bob.

![The Clean Architecture "onion"](http://blog.cleancoder.com/uncle-bob/images/2012-08-13-the-clean-architecture/CleanArchitecture.jpg)

The first rule of the Clean Architecture we will formulate is:
> _Thou shall not mix responsibilities between layers of the application.
Keep a clean separation between domain knowledge, application operations and 
their runtime environment (web frameworks, database connectors, session stores,
aso)._
> — The Unknown Author of this blog

Next sections of the lecture will take you through a few examples of design
patterns, that are introduced by most known Python application frameworks.

[[1a. Django views and forms](011_django_views_and_forms.md)]

### References:
<a id="ref-1">1.</a> [Robert "Uncle Bob" Martin, The Clean Architecture](http://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
