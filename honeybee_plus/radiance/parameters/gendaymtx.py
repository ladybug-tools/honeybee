"""Radiance raytracing Parameters."""
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


# TODO: Add a check to make sure user can't set both -s and -d to True.
@frozen
class GendaymtxParameters(AdvancedRadianceParameters):
    """Radiance Parameters for grid based analysis.

    Read more:
    https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/gendaymtx.pdf


    Attributes:
        verbose_report: [-v] A boolean to indicate verbose reporting (Default: True)
        remove_header: [-h] A boolean to disable header (Default: False)
        only_direct: [-d] A boolean to only generate sun-only matrix (Default: False)
        only_sky: [-s] A boolean to only generate sky matrix with no direct sun
            (Default: False)
        rotation: [-r deg] A floating number in degrees that indicates zenith
            rotation (Default: 0)
        sky_density: [-m N] An integer to indicate number of sky patches. Default
            value of 1 generates 146 sky pacthes.
        ground_color: [-g r g b] A tuple of r, g, b values to indicate ground
            color (Default:  0.2 0.2 0.2)
        sky_color: [-c r g b] A tuple of r, g, b values to indicate sky color
            (Default: 0.960, 1.004, 1.118)
        output_format: [-o{f|d}] An integer to indicate binary output format.
            0 is double output [d] and 1 is binary float numbers (f). If you're
            running Radiance on Windows do not use this option. (Default: None)
        output_type: [-O{0|1}] An integr specifies output type. 0 generates the
            values for visible radiance whereas 1 indicates the results should
            be total solar radiance.

        * For the full list of attributes try self.parameters
        ** values between []'s indicate Radiance equivalent keys for advanced users

    Usage:

        # generate sky matrix with default values
        gmtx = GendaymtxParameters()

        # check the current values
        print(gmtx.to_rad_string())
        > -v -r 0 -m 1 -of

        # ask only for direct sun
        gmtx.only_direct = True

        # check the new values. -d is added.
        print(gmtx.to_rad_string())
        > -v -d -r 0 -m 1 -of
    """

    def __init__(self, verbose_report=True, remove_header=False, only_direct=False,
                 only_sky=False, rotation=0, sky_density=1, ground_color=None,
                 sky_color=None, output_format=None, output_type=None):
        """Init paramters."""
        AdvancedRadianceParameters.__init__(self)

        # convert user input to radiance output formats
        _output_format = {0: 'f', 1: 'd', None: None}

        # add parameters
        self.add_radiance_bool_flag('v', 'verbose reporting',
                                    attribute_name='verbose_report')
        self.verbose_report = verbose_report
        """[-v] A boolean to indicate verbose reporting (Default: True)"""

        self.add_radiance_bool_flag('h', 'disable header',
                                    attribute_name='remove_header')
        self.remove_header = remove_header
        """[-h] A boolean to disable header (Default: False)"""

        self.add_radiance_bool_flag('d', 'sun mtx only',
                                    attribute_name='only_direct')
        self.only_direct = only_direct
        """[-d] A boolean to only generate sun-only matrix (Default: False)"""

        self.add_radiance_bool_flag('s', 'sky mtx only', attribute_name='only_sky')
        self.only_sky = only_sky
        """[-s] A boolean to only generate sky matrix with no direct sun
           (Default: False)"""

        self.add_radiance_number('r', 'zenith rotation', num_type=float,
                                 attribute_name='rotation')
        self.rotation = rotation
        """[-r deg] A floating number in degrees that indicates zenith
           rotation (Default: 0)"""

        self.add_radiance_number('m', 'sky patches', num_type=int,
                                 check_positive=True,
                                 attribute_name='sky_density')
        self.sky_density = sky_density
        """ [-m N] An integer to indicate number of sky patches. Default
            value of 1 generates 146 sky pacthes."""

        self.add_radiance_tuple('g', 'ground color', valid_range=(0, 1),
                                tuple_size=3, num_type=float,
                                attribute_name='ground_color')
        self.ground_color = ground_color
        """ [-g r g b] A tuple of r, g, b values to indicate ground
            color (Default:  0.2 0.2 0.2)"""

        self.add_radiance_tuple('c', 'sky color', valid_range=(0, 1), tuple_size=3,
                                num_type=float, attribute_name='sky_color')
        self.sky_color = sky_color
        """ [-c r g b] A tuple of r, g, b values to indicate sky color
            (Default: 0.960, 1.004, 1.118)"""

        self.add_radiance_value('o', 'output format',
                                accepted_inputs=('f', 'd'), is_joined=True,
                                attribute_name='output_format')
        self.output_format = _output_format[output_format]
        """ [-o{f|d}] An integer to indicate binary output format.
            0 is double output [d] and 1 is binary float numbers (f). If you're
            running Radiance on Windows do not use this option. (Default: None)
        """

        self.add_radiance_value('O', 'radiation type',
                                accepted_inputs=(0, 1, '0', '1'), is_joined=True,
                                attribute_name='output_type')
        self.output_type = output_type
        """ [-O{0|1}] An integr specifies output type. 0 generates the
            values for visible radiance whereas 1 indicates the results should
            be total solar radiance."""

        assert self.only_direct * self.only_sky == 0, \
            "You can only set one of the only_direct and only_sky to True."
