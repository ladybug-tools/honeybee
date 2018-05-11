"""Radiance Mixpict Mixture.

http://radsite.lbl.gov/radiance/refer/ray.html#Mixpict
"""
from .mixturebase import RadianceMixture


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Mixpict(RadianceMixture):
    """Radiance Mixpict Material.

    Mixpict combines two modifiers based on a picture:

        mod mixpict id
        7+
                foreground background func pictfile
                funcfile u v transform
        0
        m A1 A2 .. Am

    The mixing coefficient function "func" takes three arguments, the red, green and
    blue values corresponding to the pixel at (u,v).
    """
    pass
