# class_extension
A mechanism for extending python classes.

Code for adding methods to classes outside of class definitions.
For reference: another version of the same idea was found, 
proposed by GVR himself:
https://mail.python.org/pipermail/python-dev/2008-January/076194.html
I'm providing this version as a slightly safer alternative.
It has various extra checks that avoid issues.

Pros:
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

Cons:
* Methods don't appear to metaclasses at class instantiation time.
    This shouldn't be a problem, as the metaclasses shouldn't 
    be concerned with methods added in this way anyway.
* Surprises developers who expect all methods to be inside a class definition.

Notes:
Monkey-patching is expressly disallowed. 
This means you can't replace an attribute on an existing class.
However, you can override a superclass method, like an ordinary class can
and you can always create a subclass and extend that.
