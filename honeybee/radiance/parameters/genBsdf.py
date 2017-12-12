# coding=utf-8
"""Radiance rcontrib Parameters."""

from ._frozen import frozen
from ._advancedparametersbase import AdvancedRadianceParameters

# TODO: Need to add the undcoumented s option.


@frozen
class GenbsdfParameters(AdvancedRadianceParameters):

    def __init__(self, num_samples=None, num_processors=None, forward_ray_trace_on=None,
                 backward_ray_trace_on=None, input_is_mgf=None, geom_unit_incl=None,
                 geom_unit_excl=None, dimensions=None,
                 tensor_tree_rank3=None, tensor_tree_rank4=None):
        """Init paramters."""
        AdvancedRadianceParameters.__init__(self)

        # add parameters
        self.add_radiance_number('c', 'number of samples', attribute_name='num_samples',
                                 num_type=int)
        self.num_samples = num_samples

        self.add_radiance_number('n', 'number of processors',
                                 attribute_name='num_processors',
                                 num_type=int)
        self.num_processors = num_processors

        self.add_radiance_number('t3', 'create a rank 3 tensor tree',
                                 attribute_name='tensor_tree_rank3',
                                 num_type=int)
        self.tensor_tree_rank3 = tensor_tree_rank3

        self.add_radiance_number('t4', 'create a rank 4 tensor tree',
                                 attribute_name='tensor_tree_rank4',
                                 num_type=int)
        self.tensor_tree_rank4 = tensor_tree_rank4

        self.add_radiance_bool_flag('forward', descriptive_name='forward ray tracing ON',
                                    attribute_name='forward_ray_trace_on',
                                    is_dual_sign=True)
        self.forward_ray_trace_on = forward_ray_trace_on

        self.add_radiance_bool_flag('backward',
                                    descriptive_name='backward ray tracing ON',
                                    attribute_name='backward_ray_trace_on',
                                    is_dual_sign=True)
        self.backward_ray_trace_on = backward_ray_trace_on

        self.add_radiance_bool_flag('mgf',
                                    descriptive_name='input geometry is mgf format',
                                    is_dual_sign=True, attribute_name='input_is_mgf')
        self.input_is_mgf = input_is_mgf

        self.add_radiance_value('geom+', 'include geometry ouput',
                                accepted_inputs=(
                                    'meter', 'foot', 'inch', 'centimeter', 'millimeter'),
                                attribute_name='geom_unit_incl',)
        self.geom_unit_incl = geom_unit_incl
        """Include geometry in ouput. The accepted inputs for this option are one from
        ('meter','foot','inch','centimeter','millimeter') """

        self.add_radiance_value('geom-', 'exclude geometry ouput',
                                accepted_inputs=(
                                    'meter', 'foot', 'inch', 'centimeter', 'millimeter'),
                                attribute_name='geom_unit_excl')
        self.geom_unit_excl = geom_unit_excl
        """Exclude geometry in ouput. The accepted inputs for this option are one from
                ('meter','foot','inch','centimeter','millimeter') """

        self.add_radiance_tuple(
            'dim',
            'dimensions',
            tuple_size=6,
            attribute_name='dimensions')
        self.dimensions = dimensions

    def to_rad_string(self):
        initial_string = AdvancedRadianceParameters.to_rad_string(self)
        initial_string = initial_string.replace('-geom+', '+geom')
        initial_string = initial_string.replace('-geom-', '-geom')

        # if self.rcontribOptions:
        #     initialString+="-r '%s'"%self.rcontribOptions.to_rad_string()

        return initial_string
