# coding=utf-8

from _commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceNumber, RadianceTuple
from ..datatype import RadianceBoolFlag

import os


class Genskyvec(RadianceCommand):

    header_suppress = RadianceBoolFlag('h', 'suppress information header')
    sky_subdivision = RadianceNumber('m', 'reinhart sky subdivision', num_type=int)
    sky_color_rgb = RadianceTuple('c', 'RGB value for sky color', tuple_size=3)
    sun_only_vector = RadianceBoolFlag('d', 'produce a sky vector with sun only')
    input_sky_file = RadiancePath('input_sky_file', 'input sky file from gensky',
                                  relative_path=None)
    output_file = RadiancePath('output_file', 'output sky vector file',
                               relative_path=None)

    def __init__(self, header_suppress=None, sky_subdivision=None, sky_color_rgb=None,
                 sun_only_vector=None, input_sky_file=None, output_file=None):

        RadianceCommand.__init__(self, executable_name='genskyvec.pl')

        self.header_suppress = header_suppress
        self.sky_subdivision = sky_subdivision
        self.sky_color_rgb = sky_color_rgb
        self.sun_only_vector = sun_only_vector
        self.input_sky_file = input_sky_file
        self.output_file = output_file

    @property
    def input_files(self):
        return self.input_sky_file.to_rad_string()

    def to_rad_string(self, relative_path=False):
        # TODO: This only works for Windows for now.
        # Need to make the path lookup thing x-platform.
        perl_path = self.normspace(self.perl_exe_path) if os.name == 'nt' else ''
        if os.name == 'nt' and not perl_path:
            raise IOError('Failed to find perl installation.\n'
                          'genskyvec.pl needs perl to run successfully.')

        exe_name = 'genskyvec.pl' if os.name == 'nt' else 'genskyvec'
        cmd_path = self.normspace(os.path.join(self.radbin_path, exe_name))

        header_suppress = self.header_suppress.to_rad_string()
        sky_sub_div = self.sky_subdivision.to_rad_string()
        sky_color = self.sky_color_rgb.to_rad_string()
        sun_only = self.sun_only_vector.to_rad_string()

        input_params = "{} {} {} {}".format(header_suppress,
                                            sky_sub_div,
                                            sky_color,
                                            sun_only)
        input_sky = self.input_sky_file.to_rad_string()
        input_sky = "< %s" % input_sky if input_sky else ''

        output = self.output_file.to_rad_string()
        output = "> %s" % output if output else ''

        rad_string = "{} {} {} {} {}".format(perl_path, cmd_path, input_params,
                                             input_sky, output)

        self.check_input_files(rad_string)

        return rad_string
