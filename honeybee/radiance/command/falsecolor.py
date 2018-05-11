# coding=utf-8
"""falsecolor - make a falsecolor Radiance picture"""

from _commandbase import RadianceCommand
from ..datatype import RadiancePath
from ..parameters.falsecolor import FalsecolorParameters

import os


class Falsecolor(RadianceCommand):
    """
    falsecolor - make a falsecolor Radiance picture
    """
    input_image_file = RadiancePath('i', 'input file', check_exists=True)
    output_file = RadiancePath('output_file', 'output file')

    def __init__(self, input_image_file=None, output_file=None,
                 falsecolor_parameters=None):
        RadianceCommand.__init__(self, executable_name='falsecolor.pl')
        self.input_image_file = input_image_file
        """The file path for which the falsecolor image is to be created."""

        self.output_file = output_file
        """The name of the output file."""

        self.falsecolor_parameters = falsecolor_parameters
        """Paramters for the falsecolor command."""

    @property
    def falsecolor_parameters(self):
        """Get and set falsecolor_parameters."""
        return self.__falsecolor_parameters

    @falsecolor_parameters.setter
    def falsecolor_parameters(self, falsecolor_param):
        self.__falsecolor_parameters = falsecolor_param if falsecolor_param is not None \
            else FalsecolorParameters()

        assert hasattr(self.falsecolor_parameters, "isRadianceParameters"), \
            "input falsecolor_parameters is not a valid parameters type."

    def to_rad_string(self, relative_path=False):
        """"Return full command as string"""
        perl_path = self.normspace(self.perl_exe_path) if os.name == 'nt' else ''
        if os.name == 'nt' and not perl_path:
            raise IOError('Failed to find perl installation.\n'
                          'genskyvec.pl needs perl to run successfully.')

        exe_name = 'falsecolor.pl' if os.name == 'nt' else 'falsecolor'
        cmd_path = self.normspace(os.path.join(self.radbin_path, exe_name))

        input_params = self.falsecolor_parameters.to_rad_string()
        input_file = self.input_image_file.to_rad_string()
        input_file = "-i %s" % input_file if input_file else ''
        output_file = self.output_file.to_rad_string().replace("output_file", '')

        rad_string = "%s %s %s > %s" % (cmd_path, input_params, input_file, output_file)

        return rad_string

    @property
    def input_files(self):
        return self.input_image_file,

    def execute(self):
        self.check_input_files(self.to_rad_string())
        RadianceCommand.execute(self)
