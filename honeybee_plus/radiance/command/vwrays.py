# coding=utf-8
from ._commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceValue
from ..parameters.vwrays import VwraysParameters

import os


class Vwrays(RadianceCommand):
    """Vwrays compute rays for a given picture or a view."""

    view_file = RadiancePath('view_file', 'view file')
    output_data_format = RadianceValue('f', 'output data format', is_joined=True)

    def __init__(self, view_file=None, vwrays_parameters=None, output_file=None,
                 output_data_format=None):
        """Init Vwrays."""
        RadianceCommand.__init__(self)

        self.view_file = view_file
        self.vwrays_parameters = vwrays_parameters
        self.output_file = output_file
        self.output_data_format = output_data_format

    @property
    def isVwraysParameters(self):
        """return True for type check."""
        return True

    @property
    def vwrays_parameters(self):
        """Get and set gendaymtx_parameters."""
        return self.__vwrays_parameters

    @vwrays_parameters.setter
    def vwrays_parameters(self, parameters):
        self.__vwrays_parameters = parameters if parameters is not None \
            else VwraysParameters()

        assert hasattr(self.vwrays_parameters, "isRadianceParameters"), \
            "input vwrays_parameters is not a valid parameters type."

    @property
    def input_files(self):
        """Input files."""
        return self.view_file.to_rad_string()

    @property
    def output_file(self):
        """Output file."""
        return self._output_file

    @output_file.setter
    def output_file(self, file_path):
        if file_path:
            self._output_file = os.path.normpath(file_path)
        else:
            self._output_file = ''

    def to_rad_string(self, relative_path=False):
        """Return full command as a string."""
        cmd_path = self.normspace(os.path.join(self.radbin_path, 'vwrays'))
        vwrays_param = self.vwrays_parameters.to_rad_string()
        view_file_path = self.view_file.to_rad_string()
        view_file = "-vf %s" % self.normspace(view_file_path) if view_file_path else ''
        output_file = "> %s" % self.output_file if self.output_file else ''
        output_data_format = self.output_data_format.to_rad_string()
        rad_string = "{0} {1} {2} {3} {4}".format(
            cmd_path, output_data_format, vwrays_param, view_file, output_file)
        self.check_input_files(rad_string)

        return rad_string
