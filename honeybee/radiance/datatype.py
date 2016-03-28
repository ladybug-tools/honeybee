# coding=utf-8
"""Descriptors, factory classes etc for the Radiance library"""

import warnings


class RadDescrDefault(object):
    """
    The default descriptor which defines the __get__ method. Since the get
    method is not likely to be fancy most descriptors can inherit this class.
    """

    def __get__(self, instance, owner):
        value = getattr(instance, self._name)
        if value is None:
            raise Exception(
                "The value for %s hasn't been specified" % self._name[1:])
        else:
            return getattr(instance, self._name)


class RadDescrNumber(RadDescrDefault):
    """
    Descriptor to set numbers.
    """

    def __init__(self, name, descriptiveName=None, numType=None,
                 checkPositive=False):

        self._name = "_" + name
        self._type = numType
        self._checkPositive = checkPositive
        self._descriptiveName = descriptiveName

    def __set__(self, instance, value):

        if value is None:
            finalValue = None
        else:
            if self._descriptiveName:
                varName = self._name[1:] + "(%s)" % self._descriptiveName
            else:
                varName = self._name[1:]

            try:
                if self._type:
                    finalValue = self._type(value)
                else:
                    if isinstance(value, str):
                        finalValue = float(value)
                if self._checkPositive:
                    msg = "The value for %s should be greater than 0." \
                          " The value specified was %s" % (varName, value)
                    assert value >= 0, msg
            except ValueError:

                msg = "The value for %s should be a number. " \
                      "%s was specified instead " % (varName, value)
                raise ValueError(msg)
            except TypeError:
                msg = "The type of input for %s should a float or int. " \
                      "%s was specified instead" % (varName, value)
                raise TypeError(msg)

        if hash(finalValue) != hash(value) and self._type:
            msg = "The expected type for %s is %s." \
                  "The provided input %s has been converted to %s" % \
                  (varName, self._type, value, finalValue)
            warnings.warn(msg)
        setattr(instance, self._name, finalValue)
