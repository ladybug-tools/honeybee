# coding=utf-8
"""Radiance rfluxmtx parameters."""

from .gridbased import GridBasedParameters
from ._frozen import frozen
from ..datatype import RadianceNumber


@frozen
class RfluxmtxParameters(GridBasedParameters):
    """Rfluxmtx parameters."""

    samplingRaysCount = RadianceNumber('c', 'number of sampling rays', numType=int)

    def __init__(self, quality=None):
        """Init parameters."""
        GridBasedParameters.__init__(self, quality)
        self.addRadianceNumber('c', descriptiveName='Sampling Rays Count',
                               attributeName="samplingRaysCount", numType=int)
        self.samplingRaysCount = None
        """-c int Number of sampling ray counts."""
