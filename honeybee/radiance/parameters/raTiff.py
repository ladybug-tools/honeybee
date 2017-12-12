# coding=utf-8
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class RaTiffParameters(AdvancedRadianceParameters):
    def __init__(self, create_grayscale=None, reverse_conversion=None, exposure=None,
                 gamma=None, compression_type=None, xyze_output_type=None):

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

        self.add_radiance_value('compress', 'compression value',
                                accepted_inputs=('z', 'L', 'l', 'f', 'w'),
                                attribute_name='compression_type')
        self.compression_type = compression_type
        """Compression type for the output TIFF file. Accepted values are z,L,l,f and w
        for LZW,SIGLOG,SIGLOG24,IEEE-floating-point and 16bit formats respectively."""

        self.add_radiance_bool_flag('x', 'XYZE Radiance format',
                                    attribute_name='xyze_output_type')
        self.xyze_output_type = xyze_output_type
        """Create an xyzeOutput format file."""
