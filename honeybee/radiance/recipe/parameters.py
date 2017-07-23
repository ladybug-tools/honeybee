"""Radiance parameters collection for recipes."""
from ..parameters.gridbased import GridBasedParameters
from ..parameters.imagebased import ImageBasedParameters
from ..parameters.rcontrib import RcontribParameters
from ..parameters.rfluxmtx import RfluxmtxParameters

from collections import namedtuple

DCDEFAULTS = (
    {'ambientAccuracy': 0.1, 'ambientDivisions': 4096, 'ambientBounces': 3,
     'limitWeight': 0.0002},
    {'ambientAccuracy': 0.05, 'ambientDivisions': 2 * 4096, 'ambientBounces': 5,
     'limitWeight': 0.0001},
    {'ambientAccuracy': 0.02, 'ambientDivisions': 4 * 4096, 'ambientBounces': 6,
     'limitWeight': 0.00001}
)

VMDEFAULTS = (
    {'ambientAccuracy': 0.1, 'ambientDivisions': 16384, 'ambientBounces': 5,
     'limitWeight': 1E-5},
    {'ambientAccuracy': 0.1, 'ambientDivisions': 16384, 'ambientBounces': 5,
     'limitWeight': 1E-5},
    {'ambientAccuracy': 0.1, 'ambientDivisions': 16384, 'ambientBounces': 5,
     'limitWeight': 1E-5}
)

DMDEFAULTS = (
    {'ambientAccuracy': 0.1, 'ambientDivisions': 1024, 'ambientBounces': 2,
     'limitWeight': 1E-5},
    {'ambientAccuracy': 0.1, 'ambientDivisions': 8 * 1024, 'ambientBounces': 4,
     'limitWeight': 1E-5},
    {'ambientAccuracy': 0.1, 'ambientDivisions': 16 * 1024, 'ambientBounces': 6,
     'limitWeight': 1E-5}
)

SMDEFAULTS = {
    'ambientAccuracy': 0, 'ambientBounces': 0, 'directJitter': 0,
    'directCertainty': 1, 'directThreshold': 0
}

Parameters = namedtuple('Parameters', ['rad', 'dmtx', 'vmtx', 'smtx'])


def getRadianceParametersGridBased(quality, recType):
    """Get Radiance parameters for grid based recipes.

    Args:
        quality: 0 > low, 1 > Medium, 2 > High
        recType: Type of recipe.
            0 > Point-in-time, 1 > Daylight Coeff., 2 > 3Phase, 3 > 5Phase

    Returns:
        radianceParameters, viewMatrixParameters, daylightMatrixParameters,
        sunMatrixParameters
    """

    if recType == 0:
        return Parameters(GridBasedParameters(quality), None, None, None)
    elif recType == 1:
        # daylight matrix
        dmtxpar = RfluxmtxParameters(quality=quality)
        for k, v in DCDEFAULTS[quality].iteritems():
            setattr(dmtxpar, k, v)

        # sun matrix
        sunmtxpar = RcontribParameters()
        for k, v in SMDEFAULTS.iteritems():
            setattr(sunmtxpar, k, v)

        # TODO(mostapha): Change the input name in dc class from radParameters to
        # daylightMatrixParameters.
        return Parameters(dmtxpar, None, None, sunmtxpar)
    else:
        # view matrix
        vmtxpar = RfluxmtxParameters(quality=quality)
        for k, v in VMDEFAULTS[quality].iteritems():
            setattr(vmtxpar, k, v)

        # daylight matrix
        dmtxpar = RfluxmtxParameters(quality=quality)
        for k, v in DMDEFAULTS[quality].iteritems():
            setattr(dmtxpar, k, v)

        # sun matrix
        sunmtxpar = RcontribParameters()
        for k, v in SMDEFAULTS.iteritems():
            setattr(sunmtxpar, k, v)

        return Parameters(None, vmtxpar, dmtxpar, sunmtxpar)


def getRadianceParametersImageBased(quality, recType):
    """Get Radiance parameters for image based recipes.

    Args:
        quality: 0 > low, 1 > Medium, 2 > High
        recType: Type of recipe.
            0 > Point-in-time, 1 > Daylight Coeff., 2 > 3Phase, 3 > 5Phase

    Returns:
        radianceParameters, viewMatrixParameters, daylightMatrixParameters
    """
    if recType == 0:
        return Parameters(ImageBasedParameters(quality), None, None, None)
    else:
        raise NotImplementedError()
