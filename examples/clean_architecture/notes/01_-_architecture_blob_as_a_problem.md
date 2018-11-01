# 1. Architecture blob as a problem

### Stating the problem

Look at following symptoms. If you experience a few of them, these articles 
are for you:
* An application that is a spaghetti of close coupled classes without clear 
responsibilities. Every new developer has to have long intro period before 
they can locate the class they are searching for, unassisted. Every regular

* A large portion of codebase can be tested only with end-to-end tests. This 
happens because the intermediate state of components of the application 
working is so hard to isolate and replicate.

* [TODO]

Do you know these symptoms? We have seen it too. Too many times.

### What's the reference point?

You could think that the problems we've stated are imminent to any software design.
So let's take a look now at this picture below. This is the basic idea of 
The Clean Architecture [[1]](#ref-1) by Uncle Bob.

![](http://blog.cleancoder.com/uncle-bob/images/2012-08-13-the-clean-architecture/CleanArchitecture.jpg)

The first rule of the Clean Architecture we will formulate is:
> Thou shall not mix responsibilities between layers of the application.
Enforce clean separation between domain, application and their environment 
(web frameworks, database connectors, session stores, aso).
 
### What's and why's

So now let's try to take some insight into a few popular design patterns 
in the environment of Python application frameworks.

##### Django Forms
[TODO]

```python
class User(Entity):
    login = string(required=True, min_len=6, max_len=16, chars=ascii_letters)
    first_name = string()
    last_name = string()
    password = string(
        required=True, min_len=6, max_len=32, chars=validation.CHARS,
        validators=[
            validation.validate_different_characters,
            validation.validate_special_chars
    ]   )  # encrypted

    last_login = datetime(required=True)
    ip = ip4(required=True)
```

##### Django ModelForms
[TODO]

### References:
<a id="ref-1">1.</a> [Robert "Uncle Bob" Martin, The Clean Architecture](http://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
