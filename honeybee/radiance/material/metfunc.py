"""Radiance Metfunc Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Metfunc
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Metfunc(RadianceMaterial):
    """Radiance Metfunc Material.

    Metfunc is identical to plasfunc and takes the same arguments, but the specular
    component is multiplied also by the material color.
    """
    pass
