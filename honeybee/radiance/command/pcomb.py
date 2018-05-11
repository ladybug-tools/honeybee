# coding=utf-8
"""pcomb - combine Radiance pictures"""

from _commandbase import RadianceCommand
from ..datatype import RadianceNumber, RadianceTuple, RadianceBoolFlag
from ..datatype import RadiancePath
from ..parameters.pcomb import PcombParameters
import os
from ... import config


class PcombImage(RadianceCommand):
    original_pixel_use = RadianceBoolFlag('o', 'use original pixels')
    scaling_factor = RadianceNumber('s', 'scaling factor')
    rgb_color_multiplier = RadianceTuple('c', 'scaling factor for rgb channels',
                                         tuple_size=3)
    input_image_file = RadiancePath('input_image_file', 'input image file')

    def __init__(self, original_pixel_use=None, scaling_factor=None,
                 rgb_color_multiplier=None, input_image_file=None):

        RadianceCommand.__init__(self, 'pcomb')
        self.original_pixel_use = original_pixel_use
        self.scaling_factor = scaling_factor
        self.rgb_color_multiplier = rgb_color_multiplier
        self.input_image_file = input_image_file

    # Overriding these properties as I don't want the script to check for
    # binaries named PcombImage in radbin !
    @property
    def radbin_path(self):
        """Get and set path to radiance binaries.
        If you set a new value the value will be changed globally.
        """
        return config.radbin_path

    @radbin_path.setter
    def radbin_path(self, path):
        # change the path in config so user need to set it up once in a single
        #  script
        config.radbin_path = path

    def to_rad_string(self, relative_path=False):
        pixel_input = self.original_pixel_use.to_rad_string()
        scl_fact = self.scaling_factor.to_rad_string()
        rgb = self.rgb_color_multiplier.to_rad_string()
        img = self.input_image_file.to_rad_string()
        rad_string = "{} {} {} {}".format(pixel_input, scl_fact, rgb, img)
        return rad_string

    @property
    def input_files(self):
        return self.input_image_file.to_rad_string()

    def execute(self):
        raise Exception('The class PcombImage cannot be executed on its own.'
                        'It is only meant to create image classes for Pcomb.')


class Pcomb(RadianceCommand):
    output_file = RadiancePath('outputImageFile', 'output image file')

    def __init__(self, image_list=None, output_file=None,
                 pcomb_parameters=None):
        RadianceCommand.__init__(self)
        self.image_list = image_list
        self.output_file = output_file
        self.pcomb_parameters = pcomb_parameters

    @property
    def image_list(self):
        return self._image_list

    @image_list.setter
    def image_list(self, images):
        self._image_list = []
        if images:
            for image in images:
                # This is probably an overkill to have the images be assigned
                # this way but doing this will reduce a lot of errors related
                # to incorrect input flags.
                assert isinstance(image, PcombImage),\
                    'The input for image_list should be a list containing ' \
                    'instances of the class PcombImage'
                self._image_list.append(image.to_rad_string())

        else:
            self._image_list = []

    @property
    def pcomb_parameters(self):
        """Get and set gendaymtx_parameters."""
        return self._pcomb_parameters

    @pcomb_parameters.setter
    def pcomb_parameters(self, parameters):
        self._pcomb_parameters = parameters or PcombParameters()

        assert hasattr(self.pcomb_parameters, "isRadianceParameters"), \
            "input pcomb_parameters is not a valid parameters type."

    @property
    def input_files(self):
        return None

    def to_rad_string(self, relative_path=False):
        """Return full command as a string"""
        cmd_path = self.normspace(os.path.join(self.radbin_path, 'pcomb'))
        pcomb_param = self.pcomb_parameters.to_rad_string()
        input_images = " ".join(self.image_list)
        op_image_path = self.output_file.to_rad_string()
        output_images = " > %s" % op_image_path if op_image_path else ''
        rad_string = "{} {} {} {}".format(cmd_path, pcomb_param, input_images,
                                          output_images)
        return ' '.join(rad_string.split())
