# coding=utf-8
"""Descriptors, factory classes etc for the Radiance library"""

import warnings
import os

__all__ = ['RadDescrPath','RadDescrNum','RadDescrBoolFlags','RadDescrNumTuple']

class RadDescrDefault(object):
    """
    The default descriptor which defines the __get__ method. Since the get
    method is not likely to be fancy most descriptors can inherit this class.
    """

    def __init__(self, name, descriptiveName=None, expectedInputs=None,
                 validRange=None):
        self._name = "_" + name
        self._descriptiveName = descriptiveName
        self._expectedInputs = expectedInputs

        if validRange:
            assert isinstance(validRange, (tuple, list)) and len(
                validRange) == 2, \
                "The input for validRange should be a tuple/list containing" \
                " expected minimum and maximum values"
            validRange = sorted(validRange)

        self._validRange = validRange

        nameString = lambda: "%s (%s)" % (
            name, descriptiveName) if descriptiveName else name

        self._nameString = nameString()

    def __get__(self, instance, owner):
        value = getattr(instance, self._name)
        if value is None:
            raise Exception(
                "The value for %s hasn't been specified" % self._nameString)
        else:
            return getattr(instance, self._name)

    def __set__(self, instance, value):
        if self._expectedInputs and value is not None:

            inputs = list(self._expectedInputs)
            if value not in inputs:
                raise ValueError("The value for %s should be one of the"
                                 " following: %s. The provided value was %s"
                                 % (self._nameString,
                                    ",".join(map(str, inputs)), value))
            setattr(instance, self._name, value)

class RadDescrBoolFlags(RadDescrDefault):
    """Descriptor for all the inputs that are boolean flags or single
    alphabets
    """
    pass


class RadDescrNum(RadDescrDefault):
    """
    Descriptor to set numbers.
    """

    def __init__(self, name, descriptiveName=None, validRange=None,
                 expectedInputs=None, numType=None, checkPositive=False, ):

        RadDescrDefault.__init__(self, name, descriptiveName, expectedInputs,
                                 validRange)
        self._checkPositive = checkPositive
        self._descriptiveName = descriptiveName
        self._type = numType

    def __set__(self, instance, value):
        if value is not None:
            RadDescrDefault.__set__(self, instance, value)
            varName = self._nameString

            if value is None:
                finalValue = None
            else:
                try:
                    if self._type:
                        finalValue = self._type(value)
                    else:
                        if isinstance(value, str):
                            finalValue = float(value)
                        else:
                            finalValue = value
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

            if self._validRange:
                minVal, maxVal = self._validRange
                if not (minVal <= finalValue <= maxVal):
                    msg = "The specified input for %s is %s. This is beyond the" \
                          " valid range. The value for %s should be between %s" \
                          " and %s" % (
                              varName, finalValue, varName, maxVal, minVal)
                    warnings.warn(msg)
            setattr(instance, self._name, finalValue)


class RadDescrNumTuple(RadDescrDefault):
    def __init__(self, name, descriptiveName=None, validRange=None,
                 expectedInputs=None, tupleSize=None, numType=None):

        RadDescrDefault.__init__(self, name, descriptiveName, expectedInputs,
                                 validRange)
        self._tupleSize = tupleSize
        self._type = numType

    def __set__(self, instance, value):
        if value is not None:
            if self._type:
                numType = self._type
            else:
                numType = float

            try:
                finalValue = value.replace(',', ' ').split()
            except AttributeError:
                finalValue = value

            finalValue = map(numType, finalValue)

            if self._tupleSize:
                assert len(finalValue) is self._tupleSize, \
                    "The number of inputs required for %s are %s. " \
                    "The provided input was %s" % \
                    (self._nameString, self._tupleSize, value)

            if self._validRange:
                minVal, maxVal = self._validRange
                allinRange = True
                for numValue in finalValue:
                    if not (minVal <= numValue <= maxVal):
                        allinRange = False
                        break
                if not allinRange:
                    msg = "The specified input for %s is %s. " \
                          "One or more numbers are not in the valid range" \
                          ". The values should be between %s and %s" \
                          % (self._nameString, finalValue, maxVal, minVal)
                    warnings.warn(msg)

            setattr(instance, self._name, finalValue)


class RadDescrPath(RadDescrDefault):
    def __init__(self, name, descriptiveName=None, expandRelative=False,
                 checkExists=False):
        RadDescrDefault.__init__(self, name, descriptiveName)
        self._expandRelative = expandRelative
        self._checkExists = checkExists

    def __set__(self, instance, value):
        if value is not None:
            assert isinstance(value, str), \
                "The input for %s should be string containing the path name. " \
                "%s was provided instead" % (self._nameString, value)

            if self._expandRelative:
                finalValue = os.path.abspath(value)
            else:
                finalValue = value

            if self._checkExists:
                if not os.path.exists(finalValue):
                    raise IOError(
                        "The specified path for %s was not found in %s" % (
                            self._nameString, finalValue))

            setattr(instance, self._name, finalValue)


class RadInputStringFormatter:
    """This class implements a bunch of static methods for formatting Radiance
    input flags. I am encapsulating them within this one class for the sake of
    clarity. The methods are static because self in this case doesn't have
    anything to do with the operation of methods in this class.
    """

    @staticmethod
    def fmtNormal(flagVal,inputVal):
        """The normal format is something like -ab 5 , -ad 100, -g 0.5 0.2 0.3
        """
        output = " -%s"%flagVal

        try:
            output += inputVal
        except TypeError: #raise if ip is not a str.
            try:
                for values in inputVal:
                    output += " %s "%values
            except TypeError: #raise if ip is not iterable.
                output += " %s "%inputVal

        return output


    @staticmethod
    def fmtJoined(flagval,inputVal):
        """ For cases like -of , -O1 etc. where everthing after the first two
         characters is input.
         """
        output = ""
        if inputVal is not None:
            if inputVal is True: #The value is set to be True instead of option.
                inputVal = ''
            output = " -%s%s "%(flagval,inputVal)
        return output

    @staticmethod
    def fmtBool(flagVal,inputVal):
        """If the input is just a normal toggle like -v or -h etc."""
        output = ""
        if inputVal is True:
            output = "-%s "%flagVal
        return output

    @staticmethod
    def fmtBoolDualSign(flagVal,inputVal):
        """If the input is just a normal toggle like -v or -h etc."""
        output = ""
        if inputVal is True:
            output = "+%s "%flagVal
        elif inputVal is False:
            output = "-%s "%flagVal
        return output
if __name__ == "__main__":
    class SomeRadianceBinary(object):
        ab = RadDescrNum('ab', 'ambinent bounces', None, [], int, True)
        dj = RadDescrNum('dj', 'source jitter')
        weaFile = RadDescrPath('weaFile', 'Weather File Path', True, True)

        def __init__(self, ab=None, dj=None, weaFile=None):
            self.ab = ab
            self.dj = dj
            self.weaFile = weaFile


    radBinary = SomeRadianceBinary(5, 1.4, r"C:\Users\Sarith\Desktop\x.rad")
    print(radBinary.dj)
