"""Radiance Parameters Base class with methods to add descriptor type parameters."""
from ._parametersbase import RadianceParameters
from ..datatype import RadiancePath, RadianceNumber, RadianceBoolFlag, \
    RadianceTuple, RadianceValue


class AdvancedRadianceParameters(RadianceParameters):
    """Radiance Parameters Base class with methods to add descriptor type parameters.

    Usage:

        class CustomParameters(AdvancedRadianceParameters):
            pass

        rp = CustomParameters()
        rp.addRadianceNumber('ab', 'ambient bounces')
        rp.ab = 20
        rp.addRadianceValue('o', 'o f', isJoined=True)
        rp.o = f
        rp.addRadianceTuple('c', 'color', numType=int)
        rp.c = (0, 0, 254)
        rp.addRadianceBoolFlag('I', 'irradiance switch', isDualSign=True)
        rp.I = True

        print rp.toRadString()
        > -ab 20 -of -c 0 0 254 +I
    """

    def __init__(self):
        """Init parameters."""
        RadianceParameters.__init__(self)

    def __setattribute(self, name, value, attributeName=None):
        _attrname = attributeName if attributeName is not None else name

        # unfreeze the class so the new attribute can be added
        self.tryToUnfreeze()
        try:
            setattr(self.__class__, _attrname, value)
            # add name of the attribute to default parameters
            self.addDefaultParameterName(_attrname, name)
        except Exception as e:
            if hasattr(self.__class__, _attrname):
                self.addDefaultParameterName(_attrname, name)
            # this is useful for cases that the environment caches the classes
            # Grasshopper and Dynamo included
            else:
                raise Exception(e)
        finally:
            self.freeze()

    def addRadianceNumber(self, name, descriptiveName=None, validRange=None,
                          acceptedInputs=None, numType=None, checkPositive=False,
                          attributeName=None):
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

            attributeName: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        self.__setattribute(name,
                            RadianceNumber(name, descriptiveName, validRange,
                                           acceptedInputs, numType,
                                           checkPositive),
                            attributeName
                            )

    def addRadianceValue(self, name, descriptiveName=None, acceptedInputs=None,
                         isJoined=False, attributeName=None):
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

            isJoined: Set to True if the Boolean should be returned as a joined
                output (i.e. -of, -od) (Default: False)

            attributeName: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        self.__setattribute(name,
                            RadianceValue(name, descriptiveName, acceptedInputs,
                                          None, isJoined),
                            attributeName
                            )

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
        self.__setattribute(name,
                            RadiancePath(name, descriptiveName, relativePath,
                                         checkExists, extension),
                            attributeName
                            )

    def addRadianceBoolFlag(self, name, descriptiveName=None, isDualSign=False,
                            attributeName=None):
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

            isDualSign: Set to True if the Boolean should return +/- value.
                (i.e. +I/-I) (Default: False)

            attributeName: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        self.__setattribute(name,
                            RadianceBoolFlag(name, descriptiveName, None,
                                             isDualSign),
                            attributeName
                            )

    def addRadianceTuple(self, name, descriptiveName=None, validRange=None,
                         acceptedInputs=None, tupleSize=None, numType=None,
                         attributeName=None):
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

            attributeName: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        self.__setattribute(name,
                            RadianceTuple(name, descriptiveName, validRange,
                                          acceptedInputs, tupleSize, numType),
                            attributeName
                            )

    @classmethod
    def checkIncompatibleInputs(self, *args):
        """This method maybe used to check for inputs that are mutually incompatible.
        For example, a sky cannot be cloudy and clear at the same time. So, the idea is
        to specify those inputs as args and then check that no more than one of them
        is set during runtime.

        A recommended way to use this method is to call it by reimplementing toRadString.

        One usecase can be found in gendaylit.
        """
        if any(args):
            inputValues = ['"%s"' % value for value in args if value]
            assert len(inputValues) < 2,\
                'Only one of these inputs can be specified at any given time: ' \
                '%s' % ", ".join(map(str, inputValues))

        return None
