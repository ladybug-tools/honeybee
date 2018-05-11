# coding=utf-8
"""ra_bmp"""

from _commandbase import RadianceCommand
import os
from ..parameters.raTiff import RaTiffParameters
from ..datatype import RadiancePath


class RaTiff(RadianceCommand):
    input_hdr_file = RadiancePath('inputHdr', 'inputHDR file')
    output_tiff_file = RadiancePath('outputTiff', 'output TIFF file', extension='.tiff')

    def __init__(self, input_hdr_file=None, output_tiff_file=None,
                 ra_tiff_parameters=None):
        RadianceCommand.__init__(self, executable_name='ra_tiff.exe')
        self.input_hdr_file = input_hdr_file
        """Path for input HDR file"""
        self.output_tiff_file = output_tiff_file
        """Path for output tiff file"""

        self.ra_tiff_parameters = ra_tiff_parameters
        """An instance of RaTiff parameters"""

    @property
    def ra_tiff_parameters(self):
        """Get and set ra_tiff_parameters."""
        return self.__ra_tiff_parameters

    @ra_tiff_parameters.setter
    def ra_tiff_parameters(self, ra_tiff_param):
        self.__ra_tiff_parameters = ra_tiff_param if ra_tiff_param is not None \
            else RaTiffParameters()

        assert hasattr(self.ra_tiff_parameters, "isRadianceParameters"), \
            "input ra_tiff_parameters is not a valid parameters type."

    def to_rad_string(self, relative_path=False):
        cmd_name = self.normspace(os.path.join(self.radbin_path, 'ra_tiff'))
        params = self.ra_tiff_parameters.to_rad_string()

        # This is kind of an overkill to fix compression parameters,
        # It checks if the compressiion option is specified and then fixes the flag.
        # This can be done through the setter as well but the issue there is it makes the
        # interface really clunky wherein just one attribute is in the main class and
        # everything else is in params.
        if '-compress' in params:
            params_split = params.split()
            flag_index = params_split.index('-compress')
            flag_value = '-' + params_split[flag_index + 1]
            params_split[flag_index + 1] = flag_value
            params_split.pop(flag_index)
            params = " ".join(params_split)

        input_file = self.input_hdr_file.to_rad_string()
        output_file = self.output_tiff_file.to_rad_string()

        rad_string = "%s %s %s %s" % (cmd_name, params, input_file, output_file)

        return rad_string

    @property
    def input_files(self):
        return self.input_hdr_file,
