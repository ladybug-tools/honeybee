# coding=utf-8
"""Radiance rcontrib Parameters."""
from gridbased import GridBasedParameters
from ._frozen import frozen


# TODO: Implement the rest of rcontrib options
@frozen
class RcontribParameters(GridBasedParameters):
    """Radiance Parameters for rcontrib command including rtrace parameters.

    Read more:
    https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/rcontrib.pdf

    Attributes:
        modFile: [-M file] File path to a file with a list of modifiers
            (Default: None)

        * For the full list of attributes try self.parameters
        ** values between []'s indicate Radiance equivalent keys for advanced users

    Usage:

        # generate sky matrix with default values
        rcp = RcontribParameters()

        # paramters returns an empty string which means rcontrib will use
        # default values.
        print rcp.toRadString()
        >

        # add modifiers file
        rcp.modFile = "c:/ladybug/suns.txt"

        # set number of ambient bounces and ambient divisions
        # these are rtrace (gridbased) paramters
        rcp.ab = 0
        rcp.ad = 10000
        rcp.I = True

        # check radiance parameters with the new values
        print rcp.toRadString()
        > -ab 0 -ad 10000 -M c:/ladybug/suns.txt -I

        # or you can set all the parameter for rtrace based on quality
        rcp.quality = 1
        print rcp.toRadString()
        > -aa 0.2 -ab 0 -ad 10000 -M c:/ladybug/suns.txt -I -dc 0.5 -st 0.5 -lw 0.01 -as 2048 -ar 64 -lr 6 -dt 0.25 -dr 1 -ds 0.25 -dp 256
    """

    def __init__(self, modFile=None):
        """Init paramters."""
        GridBasedParameters.__init__(self)

        # add parameters
        self.addRadianceValue('M', 'modifiers file', attributeName='modFile')
        self.modFile = modFile
        """[-M file] File path to a file with a list of modifiers
        (Default: None)"""
