# coding=utf-8
"""Descriptors, factory classes etc for the Radiance library"""

import warnings
import os

__all__ = ['RadiancePath', 'RadianceNumber', 'RadianceBoolFlag',
           'RadianceNumericTuple']


class RadianceDefault(object):
    """
    The default descriptor for radiance commands. Provides base case attributes
    for other descriptors.

    Attributes:
        name: Required for all cases. Name of the flag, like 'ab' for '-ab 5'
            in rtrace etc. Note that some of the radiance flags are actually
            keywords in python. For example -or in rcollate or -as in rtrace.
            In such cases the name of the flag should be specified as orX or
            asX respectively. Refer the rcollate definition for an example.

        descriptiveName: This is the human-readable name of the flag. For
            example 'ambient divisions' for 'ab', 'view file' for 'vf' etc.
            These descriptions are usually available in the manual pages of
            Radiance. Although this is an optional input, for the purposes of
            debugging and readability, it is strongly suggested that this input
            be specified for all instances.

        acceptedInputs:Optional. List of inputs that are permissible for a
            particular command option. For example, the -h flag in rcollate
            only accepts 'i' or 'o' as options. So, in cases where permissible
            inputs are known it is recommended that this input be specified.If
            the user-specified input doesn't exist in _acceptedInputs then a
            value error will be raised.

        validRange: Optional. The valid range for several prominent radiance
            parameters is between 0 and 1. There are likely to be other
            parameters with similar valid ranges. If _validRange is specified,
            a warning will be issued in case the provided input is not within
            that range.
    """

    def __init__(self, name, descriptiveName=None, acceptedInputs=None,
                 validRange=None):
        """
        The constructor (__init__) initializes name, descriptiveName,
        acceptedInputs and validRange. If specified, tests if validRange is
        specified properly. Creates a readable description of the command with
        the nameString attribute.
        """
        self._name = "_" + name
        self._descriptiveName = descriptiveName
        self._acceptedInputs = acceptedInputs

        # check if the valid range is a 2-number tuple. Sort it if it isn't
        # sorted already.
        if validRange:
            assert isinstance(validRange, (tuple, list)) and len(
                validRange) == 2, \
                "The input for validRange should be a tuple/list containing" \
                " expected minimum and maximum values"
            validRange = sorted(validRange)

        self._validRange = validRange

        # create nameString.
        nameString = lambda: "%s (%s)" % (
            name, descriptiveName) if descriptiveName else name
        self._nameString = nameString()

    def __get__(self, instance, owner):
        """
        Raise an AttributeError through getattr if the value hasn't been
        specified at all. None value has no meaning in Radiance. So, if None is
        spefied as an input, then raise a standard exception. If everything is
        the way it should be, then just return the value of the attribute.
        """
        value = getattr(instance, self._name)
        if value is None:
            raise Exception(
                "The value for %s hasn't been specified" % self._nameString)
        else:
            return value

    def __set__(self, instance, value):
        """
        If _acceptedInputs is specified then check if the input is among the
        _acceptedInputs and assign it as an attribute. Else Raise a value
        error.
        """
        if self._acceptedInputs and value is not None:
            inputs = list(self._acceptedInputs)
            if value not in inputs:
                raise ValueError("The value for %s should be one of the"
                                 " following: %s. The provided value was %s"
                                 % (self._nameString,
                                    ",".join(map(str, inputs)), value))
            setattr(instance, self._name, value)


class RadianceBoolFlag(RadianceDefault):
    """This input is expected to a boolean value (i.e. True or False).

    Attributes:
        name: Required for all cases. Name of the flag, like 'ab' for '-ab 5'
            in rtrace etc. Note that some of the radiance flags are actually
            keywords in python. For example -or in rcollate or -as in rtrace.
            In such cases the name of the flag should be specified as orX or
            asX respectively. Refer the rcollate definition for an example.

        descriptiveName: This is the human-readable name of the flag. For
            example 'ambient divisions' for 'ab', 'view file' for 'vf' etc.
            These descriptions are usually available in the manual pages of
            Radiance. Although this is an optional input, for the purposes of
            debugging and readability, it is strongly suggested that this input
            be specified for all instances.

        acceptedInputs:Optional. List of inputs that are permissible for a
            particular command option. For example, the -h flag in rcollate
            only accepts 'i' or 'o' as options. So, in cases where permissible
            inputs are known it is recommended that this input be specified.If
            the user-specified input doesn't exist in _acceptedInputs then a
            value error will be raised.

        validRange: Optional. The valid range for several prominent radiance
            parameters is between 0 and 1. There are likely to be other
            parameters with similar valid ranges. If _validRange is specified,
            a warning will be issued in case the provided input is not within
            that range.
    """
    pass


class RadianceNumber(RadianceDefault):
    """
    This input is expected to be an integer or floating point number.

    Attributes:
        name: Required for all cases. Name of the flag, like 'ab' for '-ab 5'
            in rtrace etc. Note that some of the radiance flags are actually
            keywords in python. For example -or in rcollate or -as in rtrace.
            In such cases the name of the flag should be specified as orX or
            asX respectively. Refer the rcollate definition for an example.

        descriptiveName: This is the human-readable name of the flag. For
            example 'ambient divisions' for 'ab', 'view file' for 'vf' etc.
            These descriptions are usually available in the manual pages of
            Radiance. Although this is an optional input, for the purposes of
            debugging and readability, it is strongly suggested that this input
            be specified for all instances.

        acceptedInputs:Optional. List of inputs that are permissible for a
            particular command option. For example, the -h flag in rcollate
            only accepts 'i' or 'o' as options. So, in cases where permissible
            inputs are known it is recommended that this input be specified.If
            the user-specified input doesn't exist in _acceptedInputs then a
            value error will be raised.

        validRange: Optional. The valid range for several prominent radiance
            parameters is between 0 and 1. There are likely to be other
            parameters with similar valid ranges. If _validRange is specified,
            a warning will be issued in case the provided input is not within
            that range.
        checkPositive: Optional. Check if the number should be greater than
            or equal to zero.

        numType: Optional. Acceptable inputs are float or int. If specified, the
            __set__ method will ensure that the value is stored in that type.
            Also, if the number changes (for example from 4.212 to 4 due to int
            being specified as _type_), then a warning will be issued.
    """

    def __init__(self, name, descriptiveName=None, validRange=None,
                 acceptedInputs=None, numType=None, checkPositive=False, ):

        RadianceDefault.__init__(self, name, descriptiveName, acceptedInputs,
                                 validRange)
        self._checkPositive = checkPositive
        self._type = numType

    def __set__(self, instance, value):
        """Re-iplements the __set__ method by testing the numeric input,
        converting from str to float or int (if required)and checking for valid
        values.
        """
        if value is not None:
            RadianceDefault.__set__(self, instance, value)
            varName = self._nameString

            if value is None:
                finalValue = None
            else:
                try:
                    # Assign type if specified.
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
                # Value error will be raised if the input was anything else
                # other than a number.
                except ValueError:
                    msg = "The value for %s should be a number. " \
                          "%s was specified instead " % (varName, value)
                    raise ValueError(msg)
                except TypeError:
                    msg = "The type of input for %s should a float or int. " \
                          "%s was specified instead" % (varName, value)
                    raise TypeError(msg)
            # Raise a warning if the number got modified.
            if hash(finalValue) != hash(value) and self._type:
                msg = "The expected type for %s is %s." \
                      "The provided input %s has been converted to %s" % \
                      (varName, self._type, value, finalValue)
                warnings.warn(msg)

            # Raise a warning if the number isn't in the valid range.
            if self._validRange:
                minVal, maxVal = self._validRange
                if not (minVal <= finalValue <= maxVal):
                    msg = "The specified input for %s is %s. This is beyond " \
                          "the valid range. The value for %s should be " \
                          "between %s and %s" % (varName, finalValue, varName,
                                                 maxVal, minVal)
                    warnings.warn(msg)

            setattr(instance, self._name, finalValue)


class RadianceNumericTuple(RadianceDefault):
    """
    This input is expected to be a numeric tuple like (0.5,0.3,0.2) etc.

    (Attributes inherited from base-class are explained there.)
    Attributes:
        name: Required for all cases. Name of the flag, like 'ab' for '-ab 5'
            in rtrace etc. Note that some of the radiance flags are actually
            keywords in python. For example -or in rcollate or -as in rtrace.
            In such cases the name of the flag should be specified as orX or
            asX respectively. Refer the rcollate definition for an example.

        descriptiveName: This is the human-readable name of the flag. For
            example 'ambient divisions' for 'ab', 'view file' for 'vf' etc.
            These descriptions are usually available in the manual pages of
            Radiance. Although this is an optional input, for the purposes of
            debugging and readability, it is strongly suggested that this input
            be specified for all instances.

        acceptedInputs:Optional. List of inputs that are permissible for a
            particular command option. For example, the -h flag in rcollate
            only accepts 'i' or 'o' as options. So, in cases where permissible
            inputs are known it is recommended that this input be specified.If
            the user-specified input doesn't exist in _acceptedInputs then a
            value error will be raised.

        validRange: Optional. The valid range for several prominent radiance
            parameters is between 0 and 1. There are likely to be other
            parameters with similar valid ranges. If _validRange is specified,
            a warning will be issued in case the provided input is not within
            that range.
        tupleSize: Optional. Specify the number of inputs that are expected.

        numType: Optional. Acceptable inputs are float or int. If specified, the
            __set__ method will ensure that the value is stored in that type.
    """
    def __init__(self, name, descriptiveName=None, validRange=None,
                 acceptedInputs=None, tupleSize=None, numType=None):

        RadianceDefault.__init__(self, name, descriptiveName, acceptedInputs,
                                 validRange)
        self._tupleSize = tupleSize
        self._type = numType

    def __set__(self, instance, value):
        """
        Check for tuple size and valid range if specified. Parse from strings
        if input is specified as a string instead of a number.
        """
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


class RadiancePath(RadianceDefault):
    """
    This input is expected to be a file path.

    (Attributes inherited from base-class are explained there.)
    Attributes:
        name: Required for all cases. Name of the flag, like 'ab' for '-ab 5'
            in rtrace etc. Note that some of the radiance flags are actually
            keywords in python. For example -or in rcollate or -as in rtrace.
            In such cases the name of the flag should be specified as orX or
            asX respectively. Refer the rcollate definition for an example.

        descriptiveName: This is the human-readable name of the flag. For
            example 'ambient divisions' for 'ab', 'view file' for 'vf' etc.
            These descriptions are usually available in the manual pages of
            Radiance. Although this is an optional input, for the purposes of
            debugging and readability, it is strongly suggested that this input
            be specified for all instances.

        expandRelative: Optional. Make relative paths absolute.

        checkExists: Optional. Check if the file exists. Useful in the case of
            input files such as epw files etc. where it is essential for those
            files to exist before the command executes.

        extension: Optional. Test the extension of the file.
    """
    def __init__(self, name, descriptiveName=None, expandRelative=False,
                 checkExists=False, extension=None):
        RadianceDefault.__init__(self, name, descriptiveName)
        self._expandRelative = expandRelative
        self._checkExists = checkExists
        self._extension = extension

    def __set__(self, instance, value):
        """
        Run tests based on _expandRelative, _checkExists and _extension before
        assigning the value to attribute.
        """
        if value is not None:
            assert isinstance(value, str), \
                "The input for %s should be string containing the path name." \
                " %s was provided instead" % (self._nameString, value)

            if self._expandRelative:
                finalValue = os.path.abspath(value)
            else:
                finalValue = value

            if self._checkExists:
                if not os.path.exists(finalValue):
                    raise IOError(
                        "The specified path for %s was not found in %s" % (
                            self._nameString, finalValue))

            if self._extension:
                assert finalValue.lower().endswith(self._extension.lower()), \
                    "The accepted extension for %s is %s. The provided input" \
                    "was %s" % (self._nameString, self._extension, value)
            setattr(instance, self._name, finalValue)


class RadInputStringFormatter:
    """This class implements a bunch of static methods for formatting Radiance
    input flags. I am encapsulating them within this one class for the sake of
    clarity. The methods are static because self in this case doesn't have
    anything to do with the operation of methods in this class.
    """

    @staticmethod
    def normal(flagVal, inputVal):
        """The normal format is something like -ab 5 , -ad 100, -g 0.5 0.2 0.3
           Args:
               flagVal:The alphabet(s) denoting the flag. Like ab for ambient
                bounces.

               inputVal: The input value for the flag.
        """
        output = " -%s" % flagVal

        try:
            output += inputVal
        # raise if ip is not a str.
        except TypeError:
            try:
                for values in inputVal:
                    output += " %s " % values
            # raise if ip is not iterable.
            except TypeError:
                output += " %s " % inputVal

        return output

    @staticmethod
    def joined(flagVal, inputVal):
        """ For cases like -of , -O1 etc. where everthing after the first two
            characters is input.
        Args:
            flagVal: The alphabet(s) denoting the flag. Like ab for ambient
            bounces.
            inputVal: The input value for the flag.
         """
        output = ""
        if inputVal is not None:
            # The value is set to be True instead of an option.
            if inputVal is True:
                inputVal = ''
            output = " -%s%s " % (flagVal, inputVal)
        return output

    @staticmethod
    def boolean(flagVal, inputVal):
        """If the input is just a normal toggle like -v or -h etc.
        Args:
            flagVal: The alphabet(s) denoting the flag. Like ab for ambient
            bounces.
            inputVal: The input value for the flag.
        """
        output = ""
        if inputVal is True:
            output = "-%s " % flagVal
        return output

    @staticmethod
    def boolDualSign(flagVal, inputVal):
        """If the input is just a normal toggle like -v or -h etc.
        Args:
            flagVal: The alphabet(s) denoting the flag. Like ab for ambient
            bounces.
            inputVal: The input value for the flag.
        """
        output = ""
        if inputVal is True:
            output = "+%s " % flagVal
        elif inputVal is False:
            output = "-%s " % flagVal
        return output


if __name__ == "__main__":
    class SomeRadianceBinary(object):
        ab = RadianceNumber('ab', 'ambinent bounces', None, [], int, True)
        dj = RadianceNumber('dj', 'source jitter')
        weaFile = RadiancePath('weaFile', 'Weather File Path', True, True,
                               extension='.wea')

        def __init__(self, ab=None, dj=None, weaFile=None):
            self.ab = ab
            self.dj = dj
            self.weaFile = weaFile

    radBinary = SomeRadianceBinary(5, 1.4, r"C:\Users\Sarith\Desktop\x.rad")
    print(radBinary.dj)
