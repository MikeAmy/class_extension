# class_extension

__A mechanism for safely extending classes that are already defined.__

Allows adding methods to classes outside of their class definitions.

For reference: another version of the same idea was found, 
proposed by GVR himself:
https://mail.python.org/pipermail/python-dev/2008-January/076194.html
I'm providing this version as a slightly safer alternative.
It has various extra checks that avoid issues. 

The basic idea is that sometimes a class from another package needs to 
be extended to function in a way it was not originally designed for.
Although it totally fits in terms of responsibility, it just lacks the methods.
Unfortunately it is often not possible to use a subclass, because the
other package simply assumes that only their class will be used and provide
no form of dependency injection to allow a different class. The developer
of that class has no interest in your use-case and won't add methods or 
change anything for you.

Therefore a solution is to extend their class definition after the fact with
extra methods that allow the extended functionality. This is clean because
there is functional cohesion. The extra methods can live in the same file
as the code that uses them, making programs much easier to understand. They
have no place in the external project.

This follows from the well-known object-oriented programming principle,
call the Open-Closed Principle (aka OCP):- 

__A class should be open for extension but closed for modification__

You can also use this within your own projects only, to break up functionality
into different files using functional cohesion. No more horrifically-long
class definitions and instead, lots of small, clean, easy-to-read files. 
A major benefit of having lots of small files is that the chance of accidental
merge conflicts due to code movement within files is exponentially reduced.


## Usage example:

```
from another_file import ClassToBeExtended

class AdditionalMethods(
    ClassToBeExtended,
    metaclass=ClassExtension
):
    def additional_method(...):
        ...
        
# or, simpler way for single methods:

@add_method(ClassToBeExtended)
def another_method(self, ...):
    ...

# there is also add_attribute(Class, name, attribute)
```

## Pros:
* Promotes functional cohesion; 
    Cross-class inter-dependant code can stay together,
    easing understanding (only need to refer to one file to 
    see how something works or make changes).
* Actually safer than python's class definition mechanism due 
    to the existing-name-check assertion. i.e. we can't define
    something twice with extensions, but we can with ordinary
    classes.
* Provides a way to avoid circular imports when adding methods.
    This can be a huge benefit for a large project.
* Provides a good way to extend classes from external libraries.
    This can also be a nice benefit, as sometimes it's not 
    possible to use your subclass inside an external library.

## Cons:
* Methods don't appear to metaclasses at class instantiation time.
    This shouldn't be a problem, as the metaclasses shouldn't 
    be concerned with methods added in this way anyway.
* Surprises developers who expect all methods to be inside a class definition.

## The ClassExtension metaclass

This Extends (but does not monkey-patch, as in override existing methods) 
existing classes (referred to in the base types) with new attributes. 

It uses the class syntax because the class syntax is used to define what 
attribute are on a class, which is exactly what this does. 
No instantiable class is returned. I.e. the class definition generates None,
to avoid confusion of trying to use the extension as a class.

### Recommended naming standards in methods:

In class extension methods, 'self' is not used, for clarity. 
This reduces confusion about the type of 'self' in methods, because the method
is extending another classes, we don't see the class on which it is run.

Instead another name is picked, and if there is only a single class being
extended, this is the lowercase, underscore-separated name of that class. 

### Example 
```
# In file that defines purchases

class Customer(Person):
    def purchase(self, goods):
        ...


# later, in another file that deals with handling feedback

class CustomerFeedback(Customer, metaclass=ClassExtension):
    def receive_feedback(customer, feedback):  # Note: 'customer', not self.
        ...  # has access to customer fields etc.
```

If multiple classes are being extended, a meaningful name is picked.
If the extension is, in fact, very general (on multiple 'top' types), then
'self' can be used, or something appropriately specific.

The same name should be used in all methods defined within the class extension.

This improves readability by reminding the reader what the type of the
method target is, as it would not be as clear as in a regular class
definition.
 

## Notes:
Monkey-patching is expressly disallowed, and raises an exception.

Extending a class means adding new abilities to an existing class such that
it carries out its original responsibility with a different set of 
colloborators. As we are only extending, no existing code should break 
unless it is relies on hacky introspection. 
But as we say in Python, we're all consenting adults.

Modification is however, disallowed, because modification means that existing
code will very likely break. It may seem easier to fix a mistake in someone
else's library by modifying the class. Don't. Instead raise an issue on their
issue tracker with your suggested fix.

This also avoids accidental name-collisions causing strange errors if a new
version of the external class happens to add a new method with the same name
as in the class extension.

Being unable to modify means attributes on existing classes cannot be replaced.
However, you _can_ override a superclass method, like an ordinary class can
and you can always create a subclass and extend that. These are also seen as
extensions.
