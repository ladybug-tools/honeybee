from functools import wraps


def frozen(cls):
    """A decorator for making a frozen class.

    If a class is frozen attributes can only be added to the class under __init__
    The class will throw an AttributeError exception if one tries to add
    new attributes to the class.

    You can use `unfreeze` method to unfreeze the class and add an attribute
    and freeze it back using `freeze` class.

    This example if modified from:
    http://stackoverflow.com/questions/3603502/prevent-creating-new-attributes-outside-init

    Usage:

        @frozen
        class Foo(object):
            def __init__(self):
                self.bar = 10

        foo = Foo()
        foo.bar = 42
        try:
            foo.foobar = 24
        except AttributeError as e:
            print(e)

        # unfreeze and assigne the value
        foo.unfreeze()
        foo.foobar = 24
        foo.freeze()

        print(foo.foobar)

        > foobar is not a valid attribute for Foo. Failed to set foobar to 24.
          Use one of the add*** methods to add a new parameter.
        > 24
    """
    cls._frozen = False

    def frozensetattr(self, key, value):
        if self._frozen and not hasattr(self, key) and not key.startswith("_"):
            raise AttributeError(
                "{1} is not a valid parameter for {0}. Failed to set {1} to {2}."
                "\nUse `.parameters` method to see the list of available parameters."
                "\nUse one of the add*Parameters methods to add a new parameter."
                .format(cls.__name__, key, value)
            )
        else:
            object.__setattr__(self, key, value)

    def init_decorator(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.__frozen = True  # set __frozen to True for the original class
        return wrapper

    def freeze(self):
        self._frozen = True

    def unfreeze(self):
        self._frozen = False

    cls.__setattr__ = frozensetattr
    cls.__init__ = init_decorator(cls.__init__)
    cls.freeze = freeze
    cls.unfreeze = unfreeze
    return cls
