# coding=utf-8
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class PcombParameters(AdvancedRadianceParameters):

    def __init__(self, header_suppress=None, warnings_suppress=None, x_resolution=None,
                 y_resolution=None, function_file=None, expression=None):
        """Init paramters."""
        AdvancedRadianceParameters.__init__(self)

        self.add_radiance_bool_flag('h', 'suppress header information',
                                    attribute_name='header_suppress')
        self.header_suppress = header_suppress

        self.add_radiance_bool_flag('w', 'suppress header information',
                                    attribute_name='warnings_suppress')
        self.warnings_suppress = warnings_suppress

        # Note about resolutions: The resolution input also accepts inputs
        # such as xmax and ymax. So a number type alone won't be a proper input
        # for this option.
        self.add_radiance_value('x', 'output x resolution',
                                attribute_name='x_resolution')
        self.x_resolution = x_resolution

        self.add_radiance_value('y', 'output y resolution',
                                attribute_name='y_resolution')
        self.y_resolution = y_resolution

        self.add_radiance_value('f', 'function file', attribute_name='function_file')
        self.function_file = function_file

        # TODO: Check if this input for expression works using descriptors..!
        # This parameter might not work properly due to the rquirement of
        # quotes ie something like 'ro=ri(1)^4 ...' I am not sure at the
        # moment if ' or " is the right one to use. Check back when this option
        # is actually required.
        self.add_radiance_value('e', 'expression for modifying inputs',
                                attribute_name='expression')
        self.expression = expression
