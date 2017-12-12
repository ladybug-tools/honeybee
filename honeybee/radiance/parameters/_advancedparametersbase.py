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
        rp.add_radiance_number('ab', 'ambient bounces')
        rp.ab = 20
        rp.add_radiance_value('o', 'o f', is_joined=True)
        rp.o = f
        rp.add_radiance_tuple('c', 'color', num_type=int)
        rp.c = (0, 0, 254)
        rp.add_radiance_bool_flag('I', 'irradiance switch', is_dual_sign=True)
        rp.I = True

        print(rp.to_rad_string())
        > -ab 20 -of -c 0 0 254 +I
    """

    def __init__(self):
        """Init parameters."""
        RadianceParameters.__init__(self)

    def __setattribute(self, name, value, attribute_name=None):
        _attrname = attribute_name if attribute_name is not None else name

        # unfreeze the class so the new attribute can be added
        self.try_to_unfreeze()
        try:
            setattr(self.__class__, _attrname, value)
            # add name of the attribute to default parameters
            self.add_default_parameter_name(_attrname, name)
        except Exception as e:
            if hasattr(self.__class__, _attrname):
                self.add_default_parameter_name(_attrname, name)
            # this is useful for cases that the environment caches the classes
            # Grasshopper and Dynamo included
            else:
                raise Exception(e)
        finally:
            self.freeze()

    def add_radiance_number(self, name, descriptive_name=None, valid_range=None,
                            accepted_inputs=None, num_type=None, check_positive=False,
                            attribute_name=None):
        """Add a radiance number to parameters.

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

            attribute_name: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        self.__setattribute(name,
                            RadianceNumber(name, descriptive_name, valid_range,
                                           accepted_inputs, num_type,
                                           check_positive),
                            attribute_name
                            )

    def add_radiance_value(self, name, descriptive_name=None, accepted_inputs=None,
                           is_joined=False, attribute_name=None):
        """
        Add a radiance string value.

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

            is_joined: Set to True if the Boolean should be returned as a joined
                output (i.e. -of, -od) (Default: False)

            attribute_name: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        self.__setattribute(name,
                            RadianceValue(name, descriptive_name, accepted_inputs,
                                          None, is_joined),
                            attribute_name
                            )

    def add_radiance_path(self, name, descriptive_name=None, relative_path=None,
                          check_exists=False, extension=None, attribute_name=None):
        """
        Add a radiance file path.

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

            attribute_name: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        self.__setattribute(name,
                            RadiancePath(name, descriptive_name, relative_path,
                                         check_exists, extension),
                            attribute_name
                            )

    def add_radiance_bool_flag(self, name, descriptive_name=None, is_dual_sign=False,
                               attribute_name=None):
        """Add a boolean value to parameters.

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

            is_dual_sign: Set to True if the Boolean should return +/- value.
                (i.e. +I/-I) (Default: False)

            attribute_name: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        self.__setattribute(name,
                            RadianceBoolFlag(name, descriptive_name, None,
                                             is_dual_sign),
                            attribute_name
                            )

    def add_radiance_tuple(self, name, descriptive_name=None, valid_range=None,
                           accepted_inputs=None, tuple_size=None, num_type=None,
                           attribute_name=None):
        """Add a radiance numeric tuple e.g (0.5,0.3,0.2).

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

            attribute_name: Optional. A string the will be used as the attribute
                name that will be added to parameters class. If None name will be
                used insted.
        """
        # set the new attribute based on inputs
        self.__setattribute(name,
                            RadianceTuple(name, descriptive_name, valid_range,
                                          accepted_inputs, tuple_size, num_type),
                            attribute_name
                            )

    @staticmethod
    def check_incompatible_inputs(*args):
        """This method maybe used to check for inputs that are mutually incompatible.
        For example, a sky cannot be cloudy and clear at the same time. So, the idea is
        to specify those inputs as args and then check that no more than one of them
        is set during runtime.

        A recommended way to use this method is to call it by reimplementing
        to_rad_string.

        One usecase can be found in gendaylit.
        """
        if any(args):
            input_values = ['"%s"' % value for value in args if value]
            assert len(input_values) < 2,\
                'Only one of these inputs can be specified at any given time: ' \
                '%s' % ", ".join(map(str, input_values))

        return None
