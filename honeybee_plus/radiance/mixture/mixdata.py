"""Radiance Mixdata Mixture.

http://radsite.lbl.gov/radiance/refer/ray.html#Mixdata
"""
from .mixturebase import RadianceMixture


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Mixdata(RadianceMixture):
    """Radiance Mixdata Material.

    Mixdata combines two modifiers using an auxiliary data file:

        mod mixdata id
        5+n+
                foreground background func datafile
                funcfile x1 x2 .. xn transform
        0
        m A1 A2 .. Am

    """
    pass
