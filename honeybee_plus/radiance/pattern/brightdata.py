"""Radiance Brightdata Texture.

http://radsite.lbl.gov/radiance/refer/ray.html#Brightdata
"""
from .patternbase import RadiancePattern


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Brightdata(RadiancePattern):
    """Radiance Brightdata Material.

    Brightdata is like colordata, except monochromatic.

        mod brightdata id
        3+n+
                func datafile
                funcfile x1 x2 .. xn transform
        0
        m A1 A2 .. Am
    """
    pass
