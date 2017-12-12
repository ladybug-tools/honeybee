# coding=utf-8
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class RaBmpParameters(AdvancedRadianceParameters):
    def __init__(self, create_grayscale=None, reverse_conversion=None, exposure=None,
                 gamma=None, crt_primaries=None):

        AdvancedRadianceParameters.__init__(self)

        self.add_radiance_bool_flag('b', 'create an 8-bit gray scale image',
                                    attribute_name='create_grayscale')
        self.create_grayscale = create_grayscale
        """Create an eight bit grayscale image instead of a color image."""

        self.add_radiance_bool_flag('r', 'convert a bitmap to hdr',
                                    attribute_name='reverse_conversion')
        self.reverse_conversion = reverse_conversion
        """Do a reverse conversion and convert bitmap to hdr"""

        self.add_radiance_value('e', 'exposure value', attribute_name='exposure')
        self.exposure = exposure
        """Specify tonemapping method or exposure value. Accepted tone mapping methods
        are 'auto', 'human' or 'linear. Accepted exposure values are any number prefixed
        with a + or - sign (e.g. -1.2, +1.4, -3.4 etc)."""

        self.add_radiance_number('g', 'gamma correction', attribute_name='gamma')
        self.gamma = gamma
        """Gamma correction for the monitor. Default value is 2.2"""

        self.add_radiance_tuple('p', 'crt primaries', attribute_name='crt_primaries')
        self.crt_primaries = crt_primaries
        """CRT color output primaries."""
