# coding=utf-8
"""Radiance rcontrib Parameters."""
from .rtrace import RtraceParameters
from ._frozen import frozen


# TODO: Implement the rest of rcontrib options
@frozen
class RcontribParameters(RtraceParameters):
    """Radiance Parameters for rcontrib command including rtrace parameters.

    Read more:
    https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/rcontrib.pdf

    Attributes:
        mod_file: [-M file] File path to a file with a list of modifiers
            (Default: None)

        * For the full list of attributes try self.parameters
        ** values between []'s indicate Radiance equivalent keys for advanced users

    Usage:

        # generate sky matrix with default values
        rcp = RcontribParameters()

        # paramters returns an empty string which means rcontrib will use
        # default values.
        print(rcp.to_rad_string())
        >

        # add modifiers file
        rcp.mod_file = "c:/ladybug/suns.txt"

        # set number of ambient bounces and ambient divisions
        # these are rtrace (gridbased) paramters
        rcp.ab = 0
        rcp.ad = 10000
        rcp.I = True

        # check radiance parameters with the new values
        print(rcp.to_rad_string())
        > -ab 0 -ad 10000 -M c:/ladybug/suns.txt -I

        # or you can set all the parameter for rtrace based on quality
        rcp.quality = 1
        print(rcp.to_rad_string())
        > -aa 0.2 -ab 0 -ad 10000 -M c:/ladybug/suns.txt -I -dc 0.5 -st 0.5 -lw 0.01
            -as 2048 -ar 64 -lr 6 -dt 0.25 -dr 1 -ds 0.25 -dp 256
    """

    def __init__(self, mod_file=None, x=None, y=None, output_filename_format=None):
        """Init paramters."""
        RtraceParameters.__init__(self)

        # add parameters
        self.add_radiance_value('M', 'modifiers file', attribute_name='mod_file')

        # This is not clean or even the right way of doing this but a fix for now to
        # handle cases in running rcontrib on docker. What is happening here is that
        # I add ./ or .\ to the start of the path to modifier if it is located inside
        # sky folder which is the default folder for analemma and suns in all recipes.
        if mod_file and mod_file.startswith('sky'):
            mod_file = '.{}{}'.format(mod_file[3], mod_file)

        self.mod_file = mod_file
        """[-M file] File path to a file with a list of modifiers
        (Default: None)"""

        self.add_radiance_number('y', 'number of total points or pixels in y direction',
                                 attribute_name='y_dimension')
        self.y_dimension = y
        """[-y int] Y dimension of an image or number of total points in points file."""

        self.add_radiance_number('x', 'number of pixels in x direction',
                                 attribute_name='x_dimension')
        self.x_dimension = x
        """[-x int] X dimension of an image."""

        self.add_radiance_value('o', 'output file name format',
                                attribute_name='output_filename_format')
        self.output_filename_format = output_filename_format
        """[-0 str] output format e.g. %04f.hdr."""
