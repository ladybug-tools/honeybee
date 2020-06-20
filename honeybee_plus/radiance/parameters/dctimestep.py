# coding=utf-8

from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class DctimestepParameters(AdvancedRadianceParameters):

    def __init__(self, num_time_steps=None, suppress_header=None,
                 input_data_format=None, output_data_format=None):
        """Init paramters."""
        AdvancedRadianceParameters.__init__(self)

        self.add_radiance_number('n', 'number of time steps',
                                 attribute_name='num_time_steps')
        self.num_time_steps = num_time_steps

        self.add_radiance_bool_flag('h', 'suppress header',
                                    attribute_name='suppress_header')
        self.suppress_header = suppress_header

        self.add_radiance_value('i', 'input data format', is_joined=True,
                                attribute_name='input_data_format')
        self.input_data_format = input_data_format

        self.add_radiance_value('o', 'output data format', is_joined=True,
                                attribute_name='output_data_format')
        self.output_data_format = output_data_format
