"""Radiance raytracing Parameters."""
from _advancedparametersbase import AdvancedRadianceParameters


# TODO: Add a check to make sure user can't set both -s and -d to True.
class GendaymtxParameters(AdvancedRadianceParameters):
    """Radiance Parameters for grid based analysis.

    Read more:
    https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/gendaymtx.pdf


    Attributes:
        verboseReport: [-v] A boolean to indicate verbose reporting (Default: True)
        removeHeader: [-h] A boolean to disable header (Default: False)
        onlyDirect: [-d] A boolean to only generate sun-only matrix (Default: False)
        onlySky: [-s] A boolean to only generate sky matrix with no direct sun
            (Default: False)
        rotation: [-r deg] A floating number in degrees that indicates zenith
            rotation (Default: 0)
        skyDensity: [-m N] An integer to indicate number of sky patches. Default
            value of 1 generates 146 sky pacthes.
        groundColor: [-g r g b] A tuple of r, g, b values to indicate ground
            color (Default:  0.2 0.2 0.2)
        skyColor: [-c r g b] A tuple of r, g, b values to indicate sky color
            (Default: 0.960, 1.004, 1.118)
        outputFormat: [-o{f|d}] An integer to indicate binary output format.
            0 is double output [d] and 1 is binary float numbers (f). If you're
            running Radiance on Windows do not use this option. (Default: None)
        outputType: [-O{0|1}] An integr specifies output type. 0 generates the
            values for visible radiance whereas 1 indicates the results should
            be total solar radiance.

        * For the full list of attributes try self.keys
        ** values between []'s indicate Radiance equivalent keys for advanced users

    Usage:

        # generate sky matrix with default values
        gmtx = GendaymtxParameters()

        # check the current values
        print gmtx.toRadString()
        > -v -r 0 -m 1 -of

        # ask only for direct sun
        gmtx.onlyDirect = True

        # check the new values. -d is added.
        print gmtx.toRadString()
        > -v -d -r 0 -m 1 -of
    """


    def __init__(self, verboseReport=True, removeHeader=False, onlyDirect=False,
                 onlySky=False, rotation=0, skyDensity=1, groundColor=None,
                 skyColor=None, outputFormat=None, outputType=None):
        """Init paramters."""
        AdvancedRadianceParameters.__init__(self)

        # convert user input to radiance output formats
        _outputFormat = {0: 'f', 1: 'd', None: None}

        # add parameters
        self.addRadianceBoolFlag('v', 'verbose reporting',
                                 defaultValue=verboseReport,
                                 attributeName='verboseReport')

        self.addRadianceBoolFlag('h', 'disable header',
                                 defaultValue=removeHeader,
                                 attributeName='removeHeader')

        self.addRadianceBoolFlag('d', 'sun mtx only', defaultValue=onlyDirect,
                                 attributeName='onlyDirect')

        self.addRadianceBoolFlag('s', 'sky mtx only', defaultValue=onlySky,
                                 attributeName='onlySky')

        self.addRadianceNumber('r', 'zenith rotation', defaultValue=rotation,
                               numType=float, attributeName='rotation')

        self.addRadianceNumber('m', 'sky patches', defaultValue=skyDensity,
                               numType=int, checkPositive=True,
                               attributeName='skyDensity')

        self.addRadianceNumericTuple('g', 'ground color', defaultValue=groundColor,
                                     validRange=(0, 1), tupleSize=3, numType=float,
                                     attributeName='groundColor')

        self.addRadianceNumericTuple('c', 'sky color', defaultValue=skyColor,
                                     validRange=(0, 1), tupleSize=3, numType=float,
                                     attributeName='skyColor')

        self.addRadianceValue('o', 'output format',
                              defaultValue=_outputFormat[outputFormat],
                              acceptedInputs=('f', 'd'), isJoined=True,
                              attributeName='outputFormat')

        self.addRadianceValue('O', 'radiation type', defaultValue=outputType,
                              acceptedInputs=(0, 1, '0', '1'), isJoined=True,
                              attributeName='outputType')

        assert self.onlyDirect * self.onlySky == 0, \
            "You can only set one of the onlyDirect and onlySky to True."
