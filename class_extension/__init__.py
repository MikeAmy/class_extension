
"""Code for adding methods to classes outside of class definitions.

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

"""

import inspect
import sys


class MonkeyPatchingNotAllowed(TypeError):
    pass


# These names are things set by python in a class definition 
# and are to be ignored;
PYTHON_PRIVATE_NAMES = set(
    (
        '__module__', 
        '__metaclass__', 
        '__doc__'
    )
)


class ClassExtension(type):
    """Extends (but does not monkey-patch, as in override existing methods) 
    existing classes (referred to in the base types) 
    with new attributes. 

    It uses the class syntax because the class syntax is used to define what 
    attribute are on a class, which is exactly what this does. 
    No instantiable class is returned.

    Makes adding a group of related attributes onto an existing class a bit cleaner.

    Recommended naming standards in methods:

    In class extension definitions, for clarity, i.e. to avoid confusion in the
    type of 'self' in methods (because the method is being added to other
    classes, we don't see the class on which it is run) the standard is that
    'self' is not usually used as the name of the target object in method
    definitions.

    Instead another name is picked, and if there is only a single class being
    extended, this is the lowercase, underscore-separated name of that class. 

    E.g. 
    
    class Car(Vehicle):
        pass

    class Generator(Car):
        __metaclass__ = ClassExtension
    
        def use_as_generator(car, wires):
            ...

    If multiple classes are being extended, a meaningful name is picked.
    If the extension is, in fact, very general (on multiple 'top' types), then
    'self' can be used.

    The same name should be used in all methods defined within the class extension.

    This improves readability by reminding the reader what the type of the
    method target is, as it would not be as clear as in a regular class
    definition.

    """
    def __new__(Class, name, classes_to_extend, attributes_to_add_to_classes):
        for existing_class in classes_to_extend:
            if existing_class is object:
                raise Exception(
                    u"{} must specify which non-builtin classes to extend.".format(
                        name
                    )
                )
        for attribute_name, attribute in attributes_to_add_to_classes.iteritems():
            if attribute_name not in PYTHON_PRIVATE_NAMES:
                for class_or_object in classes_or_objects:
                    # pytest assertion.rewrite causes abnormal imports.
                    # that's OK, it only affects pytest test output.
                    if 'pytest' not in sys.modules:
                        attribute_dict = class_or_object.__dict__
                        if attribute_name in attribute_dict:
                            already_added_value = attribute_dict[attribute_name]
                            raise MonkeyPatchingNotAllowed(
                                u"{} already has an attribute '{}':\n{}\n{}.\n"
                                u"You can consider overriding in a sub-class.".format(
                                    class_or_object,
                                    attribute_name,
                                    inspect.getmodule(attribute_value),
                                    already_added_value
                                )
                            )
                        else:
                            setattr(class_or_object, attribute_name, attribute_value)
                add_attribute(classes_to_extend, attribute_name, attribute)
        # This is not an instantiable class.
        return "Uninstantiable class extension:" + name
