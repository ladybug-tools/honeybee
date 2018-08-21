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

        self.ambient_accuracy = 0.0

    @classmethod
    def direct_studies(cls, mod_file=None, x=None, y=None, output_filename_format=None):
        """Rcontrib parameters for direct studies.

        In particular this classmethod will set parameters below:
            irradiance_calc (-I) = True
            ambient_bounces (-ab) = 0
            direct_certainty (-dc) = 1
            direct_threshold (-dt) = 0
            direct_jitter (-dj) = 0
            direct_sec_relays (-dr) = 0
        """
        cls_ = cls(mod_file, x, y, output_filename_format)
        cls_.irradiance_calc = True
        cls_.ambient_bounces = 0
        cls_.direct_certainty = 1
        cls_.direct_threshold = 0
        cls_.direct_jitter = 0
        cls_.direct_sec_relays = 0
        return cls_

    def adjust_limit_weight(self):
        """Adjust lw to be 1/ad if the value is larger than 1/ad."""
        try:
            suggested_lw = 1.0 / self.ambient_divisions
        except TypeError:
            # ambient_divisions is not set
            pass
        except ZeroDivisionError:
            # ambient_divisions is set to 0!
            pass
        else:
            try:
                lw = float(self.limit_weight)
            except TypeError:
                # lw is not set so let's set the value
                print('-lw is set to %f.' % suggested_lw)
                self.limit_weight = suggested_lw
            else:
                if lw > suggested_lw:
                    print('-lw is set to %f.' % suggested_lw)
                    self.limit_weight = suggested_lw
                else:
                    print('-lw ({}) is already smaller or equal to {}.'.format(
                        self.limit_weight, suggested_lw))
