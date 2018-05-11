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

        descriptive_name: This is the human-readable name of the flag. For
            example 'ambient divisions' for 'ab', 'view file' for 'vf' etc.
            These descriptions are usually available in the manual pages of
            Radiance. Although this is an optional input, for the purposes of
            debugging and readability, it is strongly suggested that this input
            be specified for all instances.

        accepted_inputs:Optional. List of inputs that are permissible for a
            particular command option. For example, the -h flag in rcollate
            only accepts 'i' or 'o' as options. So, in cases where permissible
            inputs are known it is recommended that this input be specified.If
            the user-specified input doesn't exist in _accepted_inputs then a
            value error will be raised.

        valid_range: Optional. The valid range for several prominent radiance
            parameters is between 0 and 1. There are likely to be other
            parameters with similar valid ranges. If _valid_range is specified,
            a warning will be issued in case the provided input is not within
            that range.

        default_value: Optional. The value to be assigned in case no value is
            assigned by the user. If the default value is not specified then
            the attribute won't be considered int the creation of the
            to_rad_string string representation of the component.

        is_joined: Optional. A boolean that indicates if the name and value
            are joined in Radiance command. For instance it should be False for
            -ab 5 and should be True for -of. (Default: False)
    """

    __slots__ = ('_name', '_descriptive_name', '_accepted_inputs', '_default_value',
                 '_valid_range', '_nameString', '_is_joined')

    def __init__(self, name, descriptive_name=None, accepted_inputs=None,
                 valid_range=None, default_value=None, is_joined=False):
        """Init descriptor.

        The constructor (__init__) initializes name, descriptive_name,
        accepted_inputs and valid_range. If specified, tests if valid_range is
        specified properly. Creates a readable description of the command with
        the nameString attribute.
        """
        self._name = "_" + name
        self._descriptive_name = descriptive_name
        self._accepted_inputs = accepted_inputs
        self._default_value = default_value
        self._is_joined = is_joined
        # check if the valid range is a 2-number tuple. Sort it if it isn't
        # sorted already.
        if valid_range:
            assert isinstance(valid_range, (tuple, list)) and len(
                valid_range) == 2, \
                "The input for valid_range should be a tuple/list containing" \
                " expected minimum and maximum values"
            valid_range = sorted(valid_range)

        self._valid_range = valid_range

        # create nameString.
        self._nameString = "%s (%s)" % (name, descriptive_name) \
            if descriptive_name \
            else name

    @property
    def isRadianceDataType(self):
        """Check if object is a RadianceDataType."""
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
            if self._default_value is not None:
                value = RadianceDataType(self._name, self._default_value,
                                         self._is_joined)
            else:
                # create a radianceDataType with value None
                # to_rad_string will return and empty string
                value = RadianceDataType(self._name, None,
                                         self._is_joined)

        return value

    def __set__(self, instance, value):
        """
        If _accepted_inputs is specified then check if the input is among the
        _accepted_inputs and assign it as an attribute. Else Raise a value
        error.
        """
        if value is not None:
            if self._accepted_inputs:
                inputs = list(self._accepted_inputs)
                if value not in inputs:
                    raise ValueError("The value for %s should be one of the"
                                     " following: %s. The provided value was %s"
                                     % (self._nameString,
                                        ",".join(map(str, inputs)), value))
            if instance:
                setattr(instance, self._name,
                        RadianceDataType(self._name, value, self._is_joined))
        else:
            setattr(instance, self._name,
                    RadianceDataType(self._name, None, self._is_joined))

    def __repr__(self):
        """Value representation."""
        return str(self._default_value)


class RadianceValue(RadianceDefault):
    """A Radiance string value.

    Attributes:
        name: Required for all cases. Name of the flag, like 'ab' for '-ab 5'
            in rtrace etc. Note that some of the radiance flags are actually
            keywords in python. For example -or in rcollate or -as in rtrace.
            In such cases the name of the flag should be specified as orX or
            asX respectively. Refer the rcollate definition for an example.

        descriptive_name: This is the human-readable name of the flag. For
            example 'ambient divisions' for 'ab', 'view file' for 'vf' etc.
            These descriptions are usually available in the manual pages of
            Radiance. Although this is an optional input, for the purposes of
            debugging and readability, it is strongly suggested that this input
            be specified for all instances.

        accepted_inputs:Optional. List of inputs that are permissible for a
            particular command option. For example, the -h flag in rcollate
            only accepts 'i' or 'o' as options. So, in cases where permissible
            inputs are known it is recommended that this input be specified.If
            the user-specified input doesn't exist in _accepted_inputs then a
            value error will be raised.

        default_value: Optional. The value to be assigned in case no value is
            assigned by the user. If the default value is not specified then
            the attribute won't be considered int the creation of the
            to_rad_string string representation of the component.

        is_joined: Set to True if the Boolean should be returned as a joined
            output (i.e. -of, -od) (Default: False)

    Usage:
        o = RadianceValue('o', 'output format', default_value='f',
                          accepted_inputs=('f', 'd'))
    """

    __slots__ = ()

    def __init__(self, name, descriptive_name=None, accepted_inputs=None,
                 default_value=None, is_joined=False):
        """Init Radiance value."""
        RadianceDefault.__init__(self, name, descriptive_name=descriptive_name,
                                 accepted_inputs=accepted_inputs, valid_range=None,
                                 default_value=default_value, is_joined=is_joined)


class RadianceBoolFlag(RadianceDefault):
    """This input is expected to a boolean value (i.e. True or False).

    Attributes:
        name: Required for all cases. Name of the flag, like 'ab' for '-ab 5'
            in rtrace etc. Note that some of the radiance flags are actually
            keywords in python. For example -or in rcollate or -as in rtrace.
            In such cases the name of the flag should be specified as orX or
            asX respectively. Refer the rcollate definition for an example.

        descriptive_name: This is the human-readable name of the flag. For
            example 'ambient divisions' for 'ab', 'view file' for 'vf' etc.
            These descriptions are usually available in the manual pages of
            Radiance. Although this is an optional input, for the purposes of
            debugging and readability, it is strongly suggested that this input
            be specified for all instances.

        default_value: Optional. The value to be assigned in case no value is
            assigned by the user. If the default value is not specified then
            the attribute won't be considered int the creation of the
            to_rad_string string representation of the component.

        is_dual_sign: Set to True if the Boolean should return +/- value.
            (i.e. +I/-I) (Default: False)
    """

    __slots__ = ('_is_dual_sign',)

    def __init__(self, name, descriptive_name=None, default_value=None,
                 is_dual_sign=False):
        """Init Boolean."""
        RadianceDefault.__init__(self, name, descriptive_name=descriptive_name,
                                 accepted_inputs=(0, 1, True, False),
                                 valid_range=None, default_value=default_value)

        # This is useful for generating radiance string
        self._is_dual_sign = is_dual_sign

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
            if self._default_value is not None:
                value = RadianceBoolType(self._name, self._default_value,
                                         self._is_dual_sign)
            else:
                value = RadianceBoolType(self._name, None,
                                         self._is_dual_sign)
        return value

    def __set__(self, instance, value):
        """Overwrite set for RadianceBoolType."""
        if value is not None:
            if self._accepted_inputs:
                inputs = list(self._accepted_inputs)
                if value not in inputs:
                    raise ValueError("The value for %s should be one of the"
                                     " following: %s. The provided value was %s"
                                     % (self._nameString,
                                        ",".join(map(str, inputs)), value))

            setattr(instance, self._name,
                    RadianceBoolType(self._name, bool(value), self._is_dual_sign))


class RadianceNumber(RadianceDefault):
    """
    This input is expected to be an integer or floating point number.

    Attributes:
        name: Required for all cases. Name of the flag, like 'ab' for '-ab 5'
            in rtrace etc. Note that some of the radiance flags are actually
            keywords in python. For example -or in rcollate or -as in rtrace.
            In such cases the name of the flag should be specified as orX or
            asX respectively. Refer the rcollate definition for an example.

        descriptive_name: This is the human-readable name of the flag. For
            example 'ambient divisions' for 'ab', 'view file' for 'vf' etc.
            These descriptions are usually available in the manual pages of
            Radiance. Although this is an optional input, for the purposes of
            debugging and readability, it is strongly suggested that this input
            be specified for all instances.

        accepted_inputs:Optional. List of inputs that are permissible for a
            particular command option. For example, the -h flag in rcollate
            only accepts 'i' or 'o' as options. So, in cases where permissible
            inputs are known it is recommended that this input be specified.If
            the user-specified input doesn't exist in _accepted_inputs then a
            value error will be raised.

        valid_range: Optional. The valid range for several prominent radiance
            parameters is between 0 and 1. There are likely to be other
            parameters with similar valid ranges. If _valid_range is specified,
            a warning will be issued in case the provided input is not within
            that range.

        check_positive: Optional. Check if the number should be greater than
            or equal to zero.

        num_type: Optional. Acceptable inputs are float or int. If specified, the
            __set__ method will ensure that the value is stored in that type.
            Also, if the number changes (for example from 4.212 to 4 due to int
            being specified as _type_), then a warning will be issued.

        default_value: Optional. The value to be assigned in case no value is
            assigned by the user. If the default value is not specified then
            the attribute won't be considered int the creation of the
            to_rad_string string representation of the component.
    """

    __slots__ = ('_check_positive', '_type')

    def __init__(self, name, descriptive_name=None, valid_range=None,
                 accepted_inputs=None, num_type=None, check_positive=False,
                 default_value=None):

        RadianceDefault.__init__(self, name, descriptive_name, accepted_inputs,
                                 valid_range, default_value)

        self._check_positive = check_positive
        self._type = int if num_type is None else num_type

    def __set__(self, instance, value):
        """Re-iplements the __set__ method by testing the numeric input,
        converting from str to float or int (if required)and checking for valid
        values.
        """
        if value is not None:
            var_name = self._nameString

            if value is None:
                final_value = None
            else:
                try:
                    # Assign type if specified.
                    if self._type:
                        final_value = self._type(value)
                    else:
                        if not isinstance(value, int):
                            final_value = float(value)
                        else:
                            final_value = value
                    if self._check_positive:
                        msg = "The value for %s should be greater than 0." \
                              " The value specified was %s" % (var_name, value)
                        assert final_value >= 0, msg
                # Value error will be raised if the input was anything else
                # other than a number.
                except ValueError:
                    msg = "The value for %s should be a number. " \
                          "%s was specified instead " % (var_name, value)
                    raise ValueError(msg)
                except TypeError:
                    msg = "The type of input for %s should a float or int. " \
                          "%s was specified instead" % (var_name, value)
                    raise TypeError(msg)
                except AttributeError:
                    msg = "The type of input for %s should a float or int. " \
                          "%s was specified instead" % (var_name, value)
                    raise AttributeError(msg)

            # Raise a warning if the number got modified.
            if self._type and final_value != self._type(value):
                msg = "The expected type for %s is %s." \
                      "The provided input %s has been converted to %s" % \
                      (var_name, self._type, value, final_value)
                warnings.warn(msg)

            # Raise a warning if the number isn't in the valid range.
            if self._valid_range:
                minVal, maxVal = self._valid_range
                if not (minVal <= final_value <= maxVal):
                    msg = "The specified input for %s is %s. This is beyond " \
                          "the valid range. The value for %s should be " \
                          "between %s and %s" % (var_name, final_value, var_name,
                                                 minVal, maxVal)
                    raise ValueError(msg)

            setattr(instance, self._name, RadianceNumberType(self._name, final_value))


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

        descriptive_name: This is the human-readable name of the flag. For
            example 'ambient divisions' for 'ab', 'view file' for 'vf' etc.
            These descriptions are usually available in the manual pages of
            Radiance. Although this is an optional input, for the purposes of
            debugging and readability, it is strongly suggested that this input
            be specified for all instances.

        accepted_inputs:Optional. List of inputs that are permissible for a
            particular command option. For example, the -h flag in rcollate
            only accepts 'i' or 'o' as options. So, in cases where permissible
            inputs are known it is recommended that this input be specified.If
            the user-specified input doesn't exist in _accepted_inputs then a
            value error will be raised.

        valid_range: Optional. The valid range for several prominent radiance
            parameters is between 0 and 1. There are likely to be other
            parameters with similar valid ranges. If _valid_range is specified,
            a warning will be issued in case the provided input is not within
            that range.
        tuple_size: Optional. Specify the number of inputs that are expected.

        num_type: Optional. Acceptable inputs are float or int. If specified, the
            __set__ method will ensure that the value is stored in that type.

        default_value: Optional. The value to be assigned in case no value is
            assigned by the user. If the default value is not specified then
            the attribute won't be considered int the creation of the
            to_rad_string string representation of the component.
    """

    __slots__ = ('_tuple_size', '_type', '_test_type')

    def __init__(self, name, descriptive_name=None, valid_range=None,
                 accepted_inputs=None, tuple_size=None, num_type=None,
                 default_value=None, test_type=True):

        RadianceDefault.__init__(self, name, descriptive_name, accepted_inputs,
                                 valid_range, default_value)
        self._tuple_size = tuple_size
        self._type = num_type
        self._test_type = test_type

    def __set__(self, instance, value):
        """
        Check for tuple size and valid range if specified.

        Parse from strings if input is specified as a string instead of a number.
        """
        if value is not None:

            if self._test_type:
                if self._type:
                    num_type = self._type
                else:
                    num_type = float

            try:
                final_value = value.replace(',', ' ').split()
            except AttributeError:
                final_value = value

            try:
                if self._test_type:
                    final_value = map(num_type, final_value)
            except TypeError:
                msg = "The specified input for %s is %s. " \
                      "The value should be a list or a tuple." \
                      % (self._nameString, final_value)

                raise ValueError(msg)

            if self._tuple_size:
                assert len(final_value) == self._tuple_size, \
                    "The number of inputs required for %s are %s. " \
                    "The provided input was %s" % \
                    (self._nameString, self._tuple_size, final_value)

            if self._valid_range:
                minVal, maxVal = self._valid_range
                allin_range = True
                for numValue in final_value:
                    if not (minVal <= numValue <= maxVal):
                        allin_range = False
                        break
                if not allin_range:
                    msg = "The specified input for %s is %s. " \
                          "One or more numbers are not in the valid range" \
                          ". The values should be between %s and %s" \
                          % (self._nameString, final_value, maxVal, minVal)
                    raise ValueError(msg)

            setattr(instance, self._name,
                    RadianceDataType(self._name, tuple(final_value)))

    def __getitem__(self, i):
        """Get item i from tuple."""
        return self._default_value[i]


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

        descriptive_name: This is the human-readable name of the flag. For
            example 'ambient divisions' for 'ab', 'view file' for 'vf' etc.
            These descriptions are usually available in the manual pages of
            Radiance. Although this is an optional input, for the purposes of
            debugging and readability, it is strongly suggested that this input
            be specified for all instances.

        relative_path: Optional. Start folder for relative path. Default is None
            which returns absolute path.

        check_exists: Optional. Check if the file exists. Useful in the case of
            input files such as epw files etc. where it is essential for those
            files to exist before the command executes.

        extension: Optional. Test the extension of the file.
    """

    __slots__ = ('_relative_path', '_check_exists', '_extension')

    def __init__(self, name, descriptive_name=None, relative_path=None,
                 check_exists=False, extension=None):
        """Init path descriptor."""
        RadianceDefault.__init__(self, name, descriptive_name)
        self._relative_path = relative_path
        self._check_exists = check_exists
        self._extension = extension

    def __set__(self, instance, value):
        """Set the  value.

        Run tests based on _expandRelative, _check_exists and _extension before
        assigning the value to attribute.
        """
        if value is not None:
            value = str(value)
            assert isinstance(value, str), \
                "The input for %s should be string containing the path name." \
                " %s %s was provided instead" % (self._nameString, value, type(value))

            if self._check_exists:
                if not os.path.exists(value):
                    raise IOError(
                        "The specified path for %s was not found in %s" % (
                            self._nameString, value))

            if self._extension:
                assert value.lower().endswith(self._extension.lower()), \
                    "The accepted extension for %s is %s. The provided input" \
                    "was %s" % (self._nameString, self._extension, value)

            setattr(instance, self._name,
                    RadiancePathType(self._name, value, self._relative_path))


class RadianceDataType(object):
    """Base type for all Radiance types."""

    __slots__ = ('_name', '_value', '_is_joined')

    def __init__(self, name, value, is_joined=False):
        self._name = name.replace("_", "")
        self._value = value
        self._is_joined = is_joined

    def to_rad_string(self):
        """Return formatted value for Radiance based on the type of descriptor."""
        if self._value is None:
            return ""

        try:
            if not isinstance(self._value, basestring) \
                    and isinstance(self._value, Iterable):
                # tuple
                return "-%s %s" % (self._name, " ".join(map(str, self._value)))
            else:
                if self._is_joined:
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
        return str(self._value)

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

    __slots__ = ("_is_dual_sign",)

    def __init__(self, name, value, is_dual_sign):
        RadianceDataType.__init__(self, name, value)
        self._is_dual_sign = is_dual_sign

    def to_rad_string(self):
        """Return formatted value for Radiance based on the type of descriptor."""
        if self._value is None:
            return ""

        try:
            if self._is_dual_sign:
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

    def __init__(self, name, value, relative_path=None):
        RadianceDataType.__init__(self, name, value)
        self.relPath = relative_path
        """Start folder that relative path should be calculated from.
        If None absolute path will be returned.
        """

    def to_rad_string(self):
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
