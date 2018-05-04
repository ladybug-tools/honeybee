"""Radiance Brightfunc Pattern.

http://radsite.lbl.gov/radiance/refer/ray.html#Brightfunc
"""
from .patternbase import RadiancePattern


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Brightfunc(RadiancePattern):
    """Radiance Brightfunc Material.

    A brightfunc is the same as a colorfunc, except it is monochromatic.

        mod brightfunc id
        2+ refl funcfile transform
        0
        n A1 A2 .. An
    """
    pass
