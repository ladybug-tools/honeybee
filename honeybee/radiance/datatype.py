# coding=utf-8
"""Descriptors, factory classes etc for the Radiance library."""
import warnings
import os
from collections import Iterable

__all__ = ['RadiancePath', 'RadianceNumber', 'RadianceBoolFlag',
           'RadianceTuple', 'RadianceValue', 'RadianceReadOnly']


class RadianceDefault(object):
    """
    The default descriptor for radiance commands.

    Provides base case attributes for other descriptors.

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

        defaultValue: Optional. The value to be assigned in case no value is
            assigned by the user. If the default value is not specified then
            the attribute won't be considered int the creation of the
            toRadString string representation of the component.

        isJoined: Optional. A boolean that indicates if the name and value
            are joined in Radiance command. For instance it should be False for
            -ab 5 and should be True for -of. (Default: False)
    """

    __slots__ = ('_name', '_descriptiveName', '_acceptedInputs', '_defaultValue',
                 '_validRange', '_nameString', '_isJoined')

    def __init__(self, name, descriptiveName=None, acceptedInputs=None,
                 validRange=None, defaultValue=None, isJoined=False):
        """Init descriptor.

        The constructor (__init__) initializes name, descriptiveName,
        acceptedInputs and validRange. If specified, tests if validRange is
        specified properly. Creates a readable description of the command with
        the nameString attribute.
        """
        self._name = "_" + name
        self._descriptiveName = descriptiveName
        self._acceptedInputs = acceptedInputs
        self._defaultValue = defaultValue
        self._isJoined = isJoined
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
        self._nameString = "%s (%s)" % (name, descriptiveName) \
            if descriptiveName \
            else name

    @property
    def isRadianceDataType(self):
        """Check if object is a RadinaceDataType."""
        return True

    def __get__(self, instance, owner):
        """Return value.

        Raise an AttributeError through getattr if the value hasn't been
        specified at all. None value has no meaning in Radiance. So, if None is
        spefied as an input, then raise a standard exception. If everything is
        the way it should be, then just return the value of the attribute.
        """
        try:
            value = getattr(instance, self._name)
        except AttributeError:
            if self._defaultValue is not None:
                value = RadianceDataType(self._name, self._defaultValue,
                                         self._isJoined)
            else:
                # create a radianceDataType with value None
                # toRadString will return and empty string
                value = RadianceDataType(self._name, None,
                                         self._isJoined)

        return value

    def __set__(self, instance, value):
        """
        If _acceptedInputs is specified then check if the input is among the
        _acceptedInputs and assign it as an attribute. Else Raise a value
        error.
        """
        if value is not None:
            if self._acceptedInputs:
                inputs = list(self._acceptedInputs)
                if value not in inputs:
                    raise ValueError("The value for %s should be one of the"
                                     " following: %s. The provided value was %s"
                                     % (self._nameString,
                                        ",".join(map(str, inputs)), value))
            if instance:
                setattr(instance, self._name,
                        RadianceDataType(self._name, value, self._isJoined))
        else:
            setattr(instance, self._name,
                    RadianceDataType(self._name, None, self._isJoined))

    def __repr__(self):
        """Value representation."""
        return str(self._defaultValue)


class RadianceValue(RadianceDefault):
    """A Radiance string value.

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

        defaultValue: Optional. The value to be assigned in case no value is
            assigned by the user. If the default value is not specified then
            the attribute won't be considered int the creation of the
            toRadString string representation of the component.

        isJoined: Set to True if the Boolean should be returned as a joined
            output (i.e. -of, -od) (Default: False)

    Usage:
        o = RadianceValue('o', 'output format', defaultValue='f',
                          acceptedInputs=('f', 'd'))
    """

    __slots__ = ()

    def __init__(self, name, descriptiveName=None, acceptedInputs=None,
                 defaultValue=None, isJoined=False):
        """Init Radiance value."""
        RadianceDefault.__init__(self, name, descriptiveName=descriptiveName,
                                 acceptedInputs=acceptedInputs, validRange=None,
                                 defaultValue=defaultValue, isJoined=isJoined)


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

        defaultValue: Optional. The value to be assigned in case no value is
            assigned by the user. If the default value is not specified then
            the attribute won't be considered int the creation of the
            toRadString string representation of the component.

        isDualSign: Set to True if the Boolean should return +/- value.
            (i.e. +I/-I) (Default: False)
    """

    __slots__ = ('_isDualSign',)

    def __init__(self, name, descriptiveName=None, defaultValue=None,
                 isDualSign=False):
        """Init Boolean."""
        RadianceDefault.__init__(self, name, descriptiveName=descriptiveName,
                                 acceptedInputs=(0, 1, True, False),
                                 validRange=None, defaultValue=defaultValue)

        # This is useful for generating radiance string
        self._isDualSign = isDualSign

    def __get__(self, instance, owner):
        """Return value.

        Raise an AttributeError through getattr if the value hasn't been
        specified at all. None value has no meaning in Radiance. So, if None is
        spefied as an input, then raise a standard exception. If everything is
        the way it should be, then just return the value of the attribute.
        """
        try:
            value = getattr(instance, self._name)
        except AttributeError:
            if self._defaultValue is not None:
                value = RadianceBoolType(self._name, self._defaultValue,
                                         self._isDualSign)
            else:
                value = RadianceBoolType(self._name, None,
                                         self._isDualSign)
        return value

    def __set__(self, instance, value):
        """Overwrite set for RadianceBoolType."""
        if value is not None:
            if self._acceptedInputs:
                inputs = list(self._acceptedInputs)
                if value not in inputs:
                    raise ValueError("The value for %s should be one of the"
                                     " following: %s. The provided value was %s"
                                     % (self._nameString,
                                        ",".join(map(str, inputs)), value))

            setattr(instance, self._name,
                    RadianceBoolType(self._name, bool(value), self._isDualSign))


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

        defaultValue: Optional. The value to be assigned in case no value is
            assigned by the user. If the default value is not specified then
            the attribute won't be considered int the creation of the
            toRadString string representation of the component.
    """

    __slots__ = ('_checkPositive', '_type')

    def __init__(self, name, descriptiveName=None, validRange=None,
                 acceptedInputs=None, numType=None, checkPositive=False,
                 defaultValue=None):

        RadianceDefault.__init__(self, name, descriptiveName, acceptedInputs,
                                 validRange, defaultValue)

        self._checkPositive = checkPositive
        self._type = int if numType is None else numType

    def __set__(self, instance, value):
        """Re-iplements the __set__ method by testing the numeric input,
        converting from str to float or int (if required)and checking for valid
        values.
        """
        if value is not None:
            varName = self._nameString

            if value is None:
                finalValue = None
            else:
                try:
                    # Assign type if specified.
                    if self._type:
                        finalValue = self._type(value)
                    else:
                        if not isinstance(value, int):
                            finalValue = float(value)
                        else:
                            finalValue = value
                    if self._checkPositive:
                        msg = "The value for %s should be greater than 0." \
                              " The value specified was %s" % (varName, value)
                        assert int(value) >= 0, msg
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
                except AttributeError:
                    msg = "The type of input for %s should a float or int. " \
                          "%s was specified instead" % (varName, value)
                    raise AttributeError(msg)

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
                    raise ValueError(msg)

            setattr(instance, self._name, RadianceNumberType(self._name, finalValue))


class RadianceTuple(RadianceDefault):
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

        defaultValue: Optional. The value to be assigned in case no value is
            assigned by the user. If the default value is not specified then
            the attribute won't be considered int the creation of the
            toRadString string representation of the component.
    """

    __slots__ = ('_tupleSize', '_type', '_testType')

    def __init__(self, name, descriptiveName=None, validRange=None,
                 acceptedInputs=None, tupleSize=None, numType=None,
                 defaultValue=None, testType=True):

        RadianceDefault.__init__(self, name, descriptiveName, acceptedInputs,
                                 validRange, defaultValue)
        self._tupleSize = tupleSize
        self._type = numType
        self._testType = testType

    def __set__(self, instance, value):
        """
        Check for tuple size and valid range if specified.

        Parse from strings if input is specified as a string instead of a number.
        """
        if value is not None:

            if self._testType:
                if self._type:
                    numType = self._type
                else:
                    numType = float

            try:
                finalValue = value.replace(',', ' ').split()
            except AttributeError:
                finalValue = value

            try:
                if self._testType:
                    finalValue = map(numType, finalValue)
            except TypeError:
                msg = "The specified input for %s is %s. " \
                      "The value should be a list or a tuple." \
                      % (self._nameString, finalValue)

                raise ValueError(msg)

            if self._tupleSize:
                assert len(finalValue) == self._tupleSize, \
                    "The number of inputs required for %s are %s. " \
                    "The provided input was %s" % \
                    (self._nameString, self._tupleSize, finalValue)

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
                    raise ValueError(msg)

            setattr(instance, self._name,
                    RadianceDataType(self._name, tuple(finalValue)))

    def __getitem__(self, i):
        """Get item i from tuple."""
        return self._defaultValue[i]


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

        relativePath: Optional. Start folder for relative path. Default is None
            which returns absolute path.

        checkExists: Optional. Check if the file exists. Useful in the case of
            input files such as epw files etc. where it is essential for those
            files to exist before the command executes.

        extension: Optional. Test the extension of the file.
    """

    __slots__ = ('_relativePath', '_checkExists', '_extension')

    def __init__(self, name, descriptiveName=None, relativePath=None,
                 checkExists=False, extension=None):
        """Init path descriptor."""
        RadianceDefault.__init__(self, name, descriptiveName)
        self._relativePath = relativePath
        self._checkExists = checkExists
        self._extension = extension

    def __set__(self, instance, value):
        """Set the  value.

        Run tests based on _expandRelative, _checkExists and _extension before
        assigning the value to attribute.
        """
        if value is not None:
            value = str(value)
            assert isinstance(value, str), \
                "The input for %s should be string containing the path name." \
                " %s %s was provided instead" % (self._nameString, value, type(value))

            if self._checkExists:
                if not os.path.exists(value):
                    raise IOError(
                        "The specified path for %s was not found in %s" % (
                            self._nameString, value))

            if self._extension:
                assert value.lower().endswith(self._extension.lower()), \
                    "The accepted extension for %s is %s. The provided input" \
                    "was %s" % (self._nameString, self._extension, value)

            setattr(instance, self._name,
                    RadiancePathType(self._name, value, self._relativePath))


class RadianceDataType(object):
    """Base type for all Radiance types."""

    __slots__ = ('_name', '_value', '_isJoined')

    def __init__(self, name, value, isJoined=False):
        self._name = name.replace("_", "")
        self._value = value
        self._isJoined = isJoined

    def toRadString(self):
        """Return formatted value for Radiance based on the type of descriptor."""
        if self._value is None:
            return ""

        try:
            if not isinstance(self._value, basestring) \
                    and isinstance(self._value, Iterable):
                # tuple
                return "-%s %s" % (self._name, " ".join(map(str, self._value)))
            else:
                if self._isJoined:
                    # joined strings such as -of
                    return "-%s%s" % (self._name, str(self._value))
                else:
                    # numbers
                    return "-%s %s" % (self._name, str(self._value))

        except TypeError:
            raise ValueError("Failed to set the value to {}".format(self._value))

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return self._value

    def __eq__(self, other):
        return self._value == other

    def __ne__(self, other):
        return self._value != other

    def __getitem__(self, i):
        try:
            return self._value[i]
        except Exception as e:
            raise Exception(e)


class RadianceBoolType(RadianceDataType):
    """Radiance boolean."""

    __slots__ = ("_isDualSign",)

    def __init__(self, name, value, isDualSign):
        RadianceDataType.__init__(self, name, value)
        self._isDualSign = isDualSign

    def toRadString(self):
        """Return formatted value for Radiance based on the type of descriptor."""
        if self._value is None:
            return ""

        try:
            if self._isDualSign:
                output = "+%s" % self._name if self._value is True \
                    else "-%s" % self._name
            else:
                output = "-%s" % self._name if self._value is True else ""

            return output
        except TypeError:
            raise ValueError("Failed to set the value to {}".format(self._value))

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __eq__(self, other):
        return self._value == float(other)

    def __ne__(self, other):
        return self._value != float(other)

    def __lt__(self, other):
        return self._value < other

    def __gt__(self, other):
        return self._value > other

    def __le__(self, other):
        return self._value <= other

    def __ge__(self, other):
        return self._value >= other

    def __add__(self, other):
        return self._value + other

    def __sub__(self, other):
        return self._value - other

    def __mul__(self, other):
        return self._value * other

    def __floordiv__(self, other):
        return self._value // other

    def __div__(self, other):
        return self._value / other

    def __mod__(self, other):
        return self._value % other

    def __pow__(self, other):
        return self._value ** other

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return other - self._value

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rfloordiv__(self, other):
        return other // self._value

    def __rdiv__(self, other):
        return other / self._value

    def __rmod__(self, other):
        return other % self._value

    def __rpow__(self, other):
        return other ** self._value


class RadiancePathType(RadianceDataType):
    """Radiance path."""

    __slots__ = ("relPath",)

    def __init__(self, name, value, relativePath=None):
        RadianceDataType.__init__(self, name, value)
        self.relPath = relativePath
        """Start folder that relative path should be calculated from.
        If None absolute path will be returned.
        """

    def toRadString(self):
        """Return formatted value for Radiance based on the type of descriptor."""
        if self._value is None:
            return ""

        try:
            if self.relPath:
                return os.path.relpath(self._value, self.relPath)
            else:
                return os.path.normpath(self._value)

        except TypeError:
            raise ValueError("Failed to set the value to {}".format(self._value))

    @property
    def normpath(self):
        if self._value is None:
            return None
        else:
            return os.path.normpath(self._value)


class RadianceNumberType(RadianceDataType):
    """Radiance number."""

    __slots__ = ()

    def __init__(self, name, value):
        RadianceDataType.__init__(self, name, value)

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __eq__(self, other):
        return self._value == float(other)

    def __ne__(self, other):
        return self._value != float(other)

    def __lt__(self, other):
        return self._value < other

    def __gt__(self, other):
        return self._value > other

    def __le__(self, other):
        return self._value <= other

    def __ge__(self, other):
        return self._value >= other

    def __add__(self, other):
        return self._value + other

    def __sub__(self, other):
        return self._value - other

    def __mul__(self, other):
        return self._value * other

    def __floordiv__(self, other):
        return self._value // other

    def __div__(self, other):
        return self._value / other

    def __mod__(self, other):
        return self._value % other

    def __pow__(self, other):
        return self._value ** other

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return other - self._value

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rfloordiv__(self, other):
        return other // self._value

    def __rdiv__(self, other):
        return other / self._value

    def __rmod__(self, other):
        return other % self._value

    def __rpow__(self, other):
        return other ** self._value


class RadianceReadOnly(object):
    """A descriptor for creating Readonly values."""

    def __init__(self, name):
        self._name = '_' + str(name)

    def __get__(self, instance, owner):
        return getattr(instance, self._name)

    def __set__(self, instance, value):
        # Let the value be set first time through constructor.
        # Block all other attempts.
        try:
            value = getattr(instance, self._name)
            raise Exception("The attribute %s is read only. "
                            "It's default value is %s" % (self._name[1:], value))
        except AttributeError:
            setattr(instance, self._name, value)
