"""Radiance Parameters Base class with methods to add descriptor type parameters."""
from _parametersbase import RadianceParameters
from ..datatype import RadiancePath, RadianceNumber, RadianceBoolFlag, \
    RadianceTuple, RadianceValue


# TODO: Add __new__ to create a new class for each instance. After that the
# new paramters will be added only and only to that instance of the class since
# that is the only instance that uses that unique copy of the class.
# for now I'm using setattr(self.__class__, name, RadianceNumber(name,...))
# to minimize the damage (e.g. make sure the parameter won't be added to
# RadianceParameters). If user make a subclass from this class then it should
# work as expected.

class AdvancedRadianceParameters(RadianceParameters):
    """Radiance Parameters Base class with methods to add descriptor type parameters.

    Usage:

        class CustomParameters(AdvancedRadianceParameters):
            pass

        rp = CustomParameters()
        rp.addRadianceNumber('ab', 'ambient bounces', defaultValue=20)
        rp.addRadianceValue('o', 'o f', defaultValue='f', isJoined=True)
        rp.addRadianceTuple('c', 'color', defaultValue=(0, 0, 254), numType=int)
        rp.addRadianceBoolFlag('I', 'irradiance switch', defaultValue=True, isDualSign=True)

        print rp.toRadString()

        > -ab 20 -of -c 0 0 254 +I
    """

    def __init__(self):
        """Init parameters."""
        RadianceParameters.__init__(self)

    def addRadianceNumber(self, name, descriptiveName=None, validRange=None,
                          acceptedInputs=None, numType=None, checkPositive=False,
                          defaultValue=None, attributeName=None):
        """Add a radiance number to parameters.

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

            attributeName: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        _attrname = attributeName if attributeName is not None else name
        setattr(self.__class__,
                _attrname,
                RadianceNumber(name, descriptiveName, validRange, acceptedInputs,
                               numType, checkPositive, defaultValue)
                )

        # add name of the attribute to default parameters
        self.addDefaultParameterName(_attrname, name)

    def addRadianceValue(self, name, descriptiveName=None, acceptedInputs=None,
                         defaultValue=None, isJoined=False, attributeName=None):
        """
        Add a radiance string value.

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

            attributeName: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        _attrname = attributeName if attributeName is not None else name
        setattr(self.__class__,
                _attrname,
                RadianceValue(name, descriptiveName, acceptedInputs,
                              defaultValue, isJoined)
                )

        # add name of the attribute to default parameters
        self.addDefaultParameterName(_attrname, name)

    def addRadiancePath(self, name, descriptiveName=None, relativePath=None,
                        checkExists=False, extension=None, attributeName=None):
        """
        Add a radiance file path.

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

            attributeName: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        _attrname = attributeName if attributeName is not None else name
        setattr(self.__class__,
                _attrname,
                RadiancePath(name, descriptiveName, relativePath,
                             checkExists, extension)
                )

        # add name of the attribute to default parameters
        self.addDefaultParameterName(_attrname, name)

    def addRadianceBoolFlag(self, name, descriptiveName=None, defaultValue=None,
                            isDualSign=False, attributeName=None):
        """Add a boolean value to parameters.

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

            attributeName: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        _attrname = attributeName if attributeName is not None else name
        setattr(self.__class__,
                _attrname,
                RadianceBoolFlag(name, descriptiveName, defaultValue, isDualSign)
                )

        # add name of the attribute to default parameters
        self.addDefaultParameterName(_attrname, name)

    def addRadianceTuple(self, name, descriptiveName=None, validRange=None,
                         acceptedInputs=None, tupleSize=None, numType=None,
                         defaultValue=None, attributeName=None):
        """Add a radiance numeric tuple e.g (0.5,0.3,0.2).

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

            attributeName: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        _attrname = attributeName if attributeName is not None else name
        setattr(self.__class__,
                _attrname,
                RadianceTuple(name, descriptiveName, validRange, acceptedInputs,
                              tupleSize, numType, defaultValue)
                )

        # add name of the attribute to default parameters
        self.addDefaultParameterName(_attrname, name)
