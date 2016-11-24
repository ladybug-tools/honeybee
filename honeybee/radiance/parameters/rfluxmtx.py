# coding=utf-8
"""Radiance rfluxmtx parameters."""

from .gridbased import GridBasedParameters
from ._frozen import frozen


@frozen
class RfluxmtxParameters(GridBasedParameters):
    """Rfluxmtx parameters."""

    # TODO: @sariths we need to add description for sender, receiver, octree, etc.
    def __init__(self, sender=None, receiver=None, octree=None, systemFiles=None,
                 quality=None, ambientBounces=None, ambientDivisions=None,
                 ambientSupersamples=None, ambientResolution=None, ambientAccuracy=None,
                 directJitter=None, directSampling=None, directThreshold=None,
                 directCertainty=None, directSecRelays=None, directPresampDensity=None,
                 specularThreshold=None, limitWeight=None, limitReflections=None,
                 specularSampling=None, irradianceCalc=None, uncorRandSamp=None):
        """Init parameters."""
        GridBasedParameters.__init__(
            self, quality, ambientBounces, ambientDivisions, ambientSupersamples,
            ambientResolution, ambientAccuracy, directJitter, directSampling,
            directThreshold, directCertainty, directSecRelays, directPresampDensity,
            specularThreshold, limitWeight, limitReflections, specularSampling,
            irradianceCalc, uncorRandSamp)
