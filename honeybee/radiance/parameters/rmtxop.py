# coding=utf-8
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class RmtxopParameters(AdvancedRadianceParameters):
    """Radiance parameters for the command rmtxop.

    Read more:
    http://www.radiance-online.org/learning/documentation/
    manual-pages/pdfs/rmtxop.pdf

    Attributes:
        verboseReporting: [-v] Boolean option to print each operation to stdout.
        outputFormat: [-f[a|c|d|f]] Format in which the output data should be
            written.

    Usage:
        #generate rmtxop with default parameters.
        rmtx = RmtxopParameters()

        #check current values
        print rmtx.toRadString()
        >

        #add verbose flag.
        rmtx.verboseReporting = True

        #check values again.
        print rmtx.toRadString()
        > -v

    """

    def __init__(self, verboseReporting=None, outputFormat=None,combineValues=None,
                 transposeMatrix=None):
        AdvancedRadianceParameters.__init__(self)

        self.addRadianceBoolFlag('v', 'verbose Reporting',
                                 attributeName='verboseReporting')

        self.verboseReporting = verboseReporting
        """This boolean option turns on verbose reporting, which announces each
        operation of rmtxop"""

        self.addRadianceBoolFlag('t', 'transpose matrix',
                                 attributeName='transposeMatrix')

        self.transposeMatrix = transposeMatrix
        """This boolean option transposes the matrix."""

        self.addRadianceValue('f', 'output format',
                              attributeName='outputFormat',
                              acceptedInputs=('a', 'f', 'd', 'c'),
                              isJoined=True)

        self.outputFormat = outputFormat
        """Specify the output format. Output formats correspond to a for ASCII,
        d for binary doubles, f for floats and c for RGBE colors."""

        self.addRadianceTuple('c', 'combine values',
                              attributeName='combineValues', tupleSize=3)

        self.combineValues = combineValues
