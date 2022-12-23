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

def add_attribute(classes_or_objects, attribute_name, attribute_value):
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
        setattr(class_or_object, attribute_name, attribute_value)


def add_method(*classes_or_objects):
    def accept_method(method):
        add_attribute(classes_or_objects, method.__name__, method)
    return accept_method


class ClassExtension(type):
   def __new__(Class, name, classes_to_extend, attributes_to_add_to_classes):
        for existing_class in classes_to_extend:
            if existing_class is object:
                raise Exception(
                    u"{} must specify which non-builtin classes to extend.".format(
                        name
                    )
                )
        for attribute_name, attribute in attributes_to_add_to_classes.items():
            if attribute_name not in PYTHON_PRIVATE_NAMES:
                add_attribute(classes_to_extend, attribute_name, attribute)
        # This is not an instantiable class.
        return None
