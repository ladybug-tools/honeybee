"""Radiance Transfunc Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Transfunc
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Transfunc(RadianceMaterial):
    """Radiance Transfunc Material.

    Transfunc is similar to plasfunc but with an arbitrary bidirectional transmittance
    distribution as well as a reflectance distribution. Both reflectance and
    transmittance are specified with the same function.

        mod transfunc id
        2+ brtd funcfile transform
        0
        6+ red green blue rspec trans tspec A7 ..

    Where trans is the total light transmitted and tspec is the non-Lambertian fraction
    of transmitted light. The function brtd should integrate to 1 over each projected
    hemisphere.
    """
    pass
