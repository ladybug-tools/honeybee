# coding=utf-8
"""ra_bmp"""

from _commandbase import RadianceCommand
import os
from ..parameters.raBmp import RaBmpParameters
from ..datatype import RadiancePath


class RaBmp(RadianceCommand):
    input_hdr_file = RadiancePath('inputHdr', 'inputHDR file')
    output_bmp_file = RadiancePath('outputBmp', 'output TIFF file', extension='.bmp')

    def __init__(self, input_hdr_file=None, output_bmp_file=None,
                 ra_bmp_parameters=None):
        RadianceCommand.__init__(self, executable_name='ra_bmp.exe')
        self.input_hdr_file = input_hdr_file
        """Path for input HDR file"""
        self.output_bmp_file = output_bmp_file
        """Path for output tiff file"""
        self.ra_bmp_parameters = ra_bmp_parameters
        """An instance of RaBmp parameters"""

    @property
    def ra_bmp_parameters(self):
        """Get and set ra_bmp_parameters."""
        return self.__ra_bmp_parameters

    @ra_bmp_parameters.setter
    def ra_bmp_parameters(self, ra_bmp_param):
        self.__ra_bmp_parameters = ra_bmp_param if ra_bmp_param is not None \
            else RaBmpParameters()

        assert hasattr(self.ra_bmp_parameters, "isRadianceParameters"), \
            "input ra_bmp_parameters is not a valid parameters type."

    def to_rad_string(self, relative_path=False):
        cmd_name = self.normspace(os.path.join(self.radbin_path, 'ra_bmp'))
        params = self.ra_bmp_parameters.to_rad_string()

        input_file = self.input_hdr_file.to_rad_string()
        output_file = self.output_bmp_file.to_rad_string()

        rad_string = "%s %s %s > %s" % (cmd_name, params, input_file, output_file)

        return rad_string

    @property
    def input_files(self):
        return self.input_hdr_file,
