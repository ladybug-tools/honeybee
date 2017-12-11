# !/usr/bin/env python
# -*- coding: utf-8 -*-
from _advancedparametersbase import AdvancedRadianceParameters


class RcollateParameters(AdvancedRadianceParameters):
    """Radiance parameters for rcollate.

    Note: As on Apr-10-2016, this class has been implemented to facilitate
    it's use for 3-Phase and 5-Phase method calculations. Not all the possible
    options of rcollate have been added at present.

    Read more:
    http://www.radiance-online.org/learning/documentation/manual-pages\
    pdfs/rcollate.pdf

    Attributes:
        remove_header: [-h[io]] -hi turns input header off, -ho turns ouput
            header off. -h turns both off.
        warnings_off: [-w] turn off non fatal warnings.
        output_format: [-f[afdb[N]]. Specify an output format.
        transpose: [-t] Transpose the matrix.
        input_columns: [-ic col] Size of the columns of the input matrix.
        output_columns: [-oc col] Size of the columns of the output matrix.
        input_rows: [-ir row] Size of the rows of the input matrix.
        output_rows: [-or row] Size of the rows of output matrix.

        * For the full list of attributes try self.keys
        ** values between []'s indicate Radiance equivalent keys for advanced users

    Usage:

        #Rearrange an input 10x10 matrix to 20x5 matrix.
        rcolparam = RcollateParameters()

        rcolparam.input_columns = 10
        rcolpara.input_rows = 10

        rcolparam.output_rows = 20
        rcolparam.output_columns = 5

        #Check the values.
        print(rcolparam.to_rad_string())
        > -ic 10 -ir 10 -oc 5 -or 20
    """

    def __init__(self, remove_header=None, warnings_off=None, output_format=None,
                 transpose=None, input_columns=None, output_columns=None,
                 input_rows=None, output_rows=None):
        self.remove_header = None
        """ remove_header: [-h[io]] -hi turns input header off, -ho turns ouput
            header off. -h turns both off. """

        self.warnings_off = None
        """warnings_off: [-w] turn off non fatal warnings."""

        self.output_format = None
        """output_format: [-f[afdb[N]]. Specify an output format."""

        self.transpose = None
        """transpose: [-t] Transpose the matrix."""

        self.input_columns = None
        """input_columns: [-ic col] Size of the columns of the input matrix."""

        self.output_columns = None
        """output_columns: [-oc col] Size of the columns of the output matrix."""

        self.input_rows = None
        """input_rows: [-ir row] Size of the rows of the input matrix."""

        self.output_rows = None
        """output_rows: [-or row] Size of the rows of output matrix."""

        self.add_radiance_value('h', 'remove_header', accepted_inputs=[True, 'i', 'o'],
                                default_value=remove_header, is_joined=True)
        self.add_radiance_bool_flag('w', 'warnings_off', default_value=warnings_off)
        self.add_radiance_bool_flag('t', 'transpose', default_value=transpose)
        self.add_radiance_number('ic', 'input_columns', default_value=input_columns,
                                 num_type=int)
        self.add_radiance_number('oc', 'output_columns', default_value=output_columns,
                                 num_type=int)
        self.add_radiance_number('ir', 'input_rows', default_value=input_rows,
                                 num_type=int)
        self.add_radiance_number('or', 'output_rows', default_value=output_rows,
                                 num_type=int)
