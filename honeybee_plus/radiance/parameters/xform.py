# coding=utf-8
"""Radiance xform parameters"""

from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class XformParameters(AdvancedRadianceParameters):
    def __init__(self, command_expand_prevent=None, invert_surfaces=None,
                 name_prefix_to_mod=None, mod_replace=None, argument_file=None):
        # Init parameters
        AdvancedRadianceParameters.__init__(self)

        self.add_radiance_bool_flag('c', 'do not expand commands in file',
                                    attribute_name='command_expand_prevent')
        self.command_expand_prevent = command_expand_prevent

        self.add_radiance_bool_flag('I', 'invert surfaces',
                                    attribute_name='invert_surfaces')
        self.invert_surfaces = invert_surfaces

        self.add_radiance_value('m', 'modifier to replace all modifiers',
                                attribute_name='mod_replace')
        self.mod_replace = mod_replace

        self.add_radiance_value('name_prefix_to_mod', 'prefix value to all modifiers',
                                attribute_name='name_prefix_to_mod')
        self.name_prefix_to_mod = name_prefix_to_mod

        self.add_radiance_path('argument_file', 'file that contains transforms',
                               attribute_name='argument_file')
        self.argument_file = argument_file
