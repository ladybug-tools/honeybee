"""Radiance parameters collection for recipes.


Note on default parameters for daylight coefficient based studies

    1. These parameters are meant specifically for rcontrib-based workflows and are not
        applicable to conventional rpict- and rtrace- based simulations.
    2. The values in tuples DCDEFAULTS, VMDEFAULTS are geared towards illuminance
        simulations. The values for DMDEFAULTS and SMDEFAULTS can be used with
        image-based simulations too.
    3. The value for limit-weight should be a value less than 1/ambient-divisions. The
        current values have been assigned as (1/ambient-divisions)*0.01. This should be
        taken into account if these parameters are being changed in the future.
    4. Finally, in the present scenario, there are no optimized set of parameters to
        bring any simulation results to convergence using Monte-Carlo simulations. So,
        these default values are based on best-practice discussions and experience of
        developers.
"""
from ..parameters.rtrace import RtraceParameters
from ..parameters.rpict import RpictParameters
from ..parameters.rcontrib import RcontribParameters
from ..parameters.rfluxmtx import RfluxmtxParameters

from collections import namedtuple

# ~~~~~~~~~~~STARTING DEFAULT PARAMETERS

# Illuminance based daylight-coefficients
# Parameter settings explained contextually:
# Low: Simple room with almost no external geoemtry.
# Medium: Room with some furniture, partitions with some external geometry
# (few buildings).
# High: A room within a sky-scraper with intricate furnitures, complex
# external geometry (complex fins,overhangs etc).
DCDEFAULTS = (
    {'ambient_divisions': 5000, 'ambient_bounces': 3, 'limit_weight': 0.000002,
     'sampling_rays_count': 1},
    {'ambient_divisions': 15000, 'ambient_bounces': 5, 'limit_weight': 6.67E-07,
     'sampling_rays_count': 1},
    {'ambient_divisions': 25000, 'ambient_bounces': 6, 'limit_weight': 4E-07,
     'sampling_rays_count': 1}
)

# Image-based daylight coefficients
# Parameter settings explained contextually:
#   Low: Regardless of geometry, these settings are suitable for doing a first pass
#     simulation.
#   Medium: These parameters will be enough for the results from a single room with side
#     lighting to converge.
#   High: Set these parameters for generating high-quality final renderings.
IMGDCDEFAULTS = (
    {'ambient_divisions': 1000, 'ambient_bounces': 2, 'limit_weight': 0.0001,
     'sampling_rays_count': 1},
    {'ambient_divisions': 5000, 'ambient_bounces': 4, 'limit_weight': 0.00002,
     'sampling_rays_count': 5},
    {'ambient_divisions': 15000, 'ambient_bounces': 5, 'limit_weight': 6.666E-06,
     'sampling_rays_count': 6}
)


# Image-based View Matrix parameters for Three Phase, Five Phase and F-Matrix simulations
# Parameter settings explained contextually:
#   Low: Regardless of geometry, these settings are suitable for doing a first pass
#     simulation.
#   Medium: These parameters will be enough for the results from a single room with side
#     lighting to converge.
#   High: Set these parameters for generating high-quality final renderings.
IMGVMDEFAULTS = (
    {'ambient_divisions': 1000, 'ambient_bounces': 2, 'limit_weight': 0.0001,
     'sampling_rays_count': 1},
    {'ambient_divisions': 3000, 'ambient_bounces': 4, 'limit_weight': 3.33E-05,
     'sampling_rays_count': 5},
    {'ambient_divisions': 10000, 'ambient_bounces': 5, 'limit_weight': 1E-05,
     'sampling_rays_count': 6}
)

# Illuminance based view matrix parameters.
# Parameter settings explained contextually:
# Low: Simple room with one or two glazing systems and no furniture.
# Medium: Room with partitions, furnitures etc. but no occluding surfaces for
# calculation grids.
# High: Complex room or envrionment, like an Aircraft cabin (!) with lots
# of detailing and occulding surfaces.
VMDEFAULTS = (
    {'ambient_divisions': 1000, 'ambient_bounces': 3, 'limit_weight': 0.00001},
    {'ambient_divisions': 5000, 'ambient_bounces': 5, 'limit_weight': 0.00002},
    {'ambient_divisions': 20000, 'ambient_bounces': 7, 'limit_weight': 5E-7}
)

# Daylight Matrix
# Parameter settings explained contextually:
# Low: Room is surrounded by virtually no geometry. The glazing system has a clear view
# of the sky.
# Medium: Room is surrounded by some buildings.
# High: Room is surrounded by several shapes..The glazing might not have a direct view
# of the sky.
DMDEFAULTS = (
    {'ambient_divisions': 1024, 'ambient_bounces': 2, 'limit_weight': 0.00001,
     'sampling_rays_count': 1000},
    {'ambient_divisions': 3000, 'ambient_bounces': 4, 'limit_weight': 3.33E-06,
     'sampling_rays_count': 1000},
    {'ambient_divisions': 10000, 'ambient_bounces': 6, 'limit_weight': 0.000001,
     'sampling_rays_count': 1000}
)

# Sun-matrix
# These settings are set such that every solar disc disc in the celestial hemisphere is
# accounted for and participates in shadow testing.
SMDEFAULTS = {'ambient_bounces': 0, 'direct_jitter': 0, 'direct_certainty': 1,
              'direct_threshold': 0}

# ~~~~~~~~~~~ENDING DEFAULT PARAMETERS

Parameters = namedtuple('Parameters', ['rad', 'vmtx', 'dmtx', 'smtx'])


def get_radiance_parameters_grid_based(quality, rec_type):
    """Get Radiance parameters for grid based recipes.

    Args:
        quality: 0 > low, 1 > Medium, 2 > High
        rec_type: Type of recipe.
            0 > Point-in-time, 1 > Daylight Coeff., 2 > 3Phase, 3 > 5Phase

    Returns:
        radiance_parameters, viewMatrixParameters, daylight_matrixParameters,
        sun_matrixParameters
    """

    if rec_type == 0:
        return Parameters(RtraceParameters(quality), None, None, None)
    elif rec_type == 1:
        # daylight matrix
        dmtxpar = RfluxmtxParameters(quality=quality)
        for k, v in DCDEFAULTS[quality].iteritems():
            setattr(dmtxpar, k, v)

        # sun matrix
        sunmtxpar = RcontribParameters()
        for k, v in SMDEFAULTS.iteritems():
            setattr(sunmtxpar, k, v)

        return Parameters(None, None, dmtxpar, sunmtxpar)
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


def get_radiance_parameters_image_based(quality, rec_type):
    """Get Radiance parameters for image based recipes.

    Args:
        quality: 0 > low, 1 > Medium, 2 > High
        rec_type: Type of recipe.
            0 > Point-in-time, 1 > Daylight Coeff., 2 > 3Phase, 3 > 5Phase

    Returns:
        radiance_parameters, viewMatrixParameters, daylight_matrixParameters
    """
    if rec_type == 0:
        return Parameters(RpictParameters(quality), None, None, None)
    elif rec_type == 1:
        # this is a place holder.
        # daylight matrix
        dmtxpar = RfluxmtxParameters(quality=quality)
        for k, v in IMGDCDEFAULTS[quality].iteritems():
            setattr(dmtxpar, k, v)

        # sun matrix
        sunmtxpar = RcontribParameters()
        for k, v in SMDEFAULTS.iteritems():
            setattr(sunmtxpar, k, v)

        return Parameters(None, None, dmtxpar, sunmtxpar)
    else:
        # view matrix
        vmtxpar = RfluxmtxParameters(quality=quality)
        for k, v in IMGVMDEFAULTS[quality].iteritems():
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
