# coding=utf-8
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class RmtxopParameters(AdvancedRadianceParameters):
    """Radiance parameters for the command rmtxop.

    Read more:
    http://www.radiance-online.org/learning/documentation\
    manual-pages/pdfs/rmtxop.pdf

    Attributes:
        verbose_reporting: [-v] Boolean option to print each operation to stdout.
        output_format: [-f[a|c|d|f]] Format in which the output data should be
            written.

    Usage:
        #generate rmtxop with default parameters.
        rmtx = RmtxopParameters()

        #check current values
        print(rmtx.to_rad_string())
        >

        #add verbose flag.
        rmtx.verbose_reporting = True

        #check values again.
        print(rmtx.to_rad_string())
        > -v

    """

    def __init__(self, verbose_reporting=None, output_format=None, combine_values=None,
                 transpose_matrix=None):
        AdvancedRadianceParameters.__init__(self)

        self.add_radiance_bool_flag('v', 'verbose Reporting',
                                    attribute_name='verbose_reporting')

        self.verbose_reporting = verbose_reporting
        """This boolean option turns on verbose reporting, which announces each
        operation of rmtxop"""

        self.add_radiance_bool_flag('t', 'transpose matrix',
                                    attribute_name='transpose_matrix')

        self.transpose_matrix = transpose_matrix
        """This boolean option transposes the matrix."""

        self.add_radiance_value('f', 'output format',
                                attribute_name='output_format',
                                accepted_inputs=('a', 'f', 'd', 'c'),
                                is_joined=True)

        self.output_format = output_format
        """Specify the output format. Output formats correspond to a for ASCII,
        d for binary doubles, f for floats and c for RGBE colors."""

        self.add_radiance_tuple('c', 'combine values',
                                attribute_name='combine_values', tuple_size=3)

        self.combine_values = combine_values
