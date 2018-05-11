"""Radiance Colorpict Pattern.

http://radsite.lbl.gov/radiance/refer/ray.html#Colorpict
"""
from .patternbase import RadiancePattern


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Colorpict(RadiancePattern):
    """Radiance Colorpict Pattern.

    Colorpict is a special case of colordata, where the pattern is a two-dimensional
    image stored in the RADIANCE picture format. The dimensions of the image data are
    determined by the picture such that the smaller dimension is always 1, and the
    other is the ratio between the larger and the smaller. For example, a 500x338
    picture would have coordinates (u,v) in the rectangle between (0,0) and (1.48,1).

        mod colorpict id
        7+
                rfunc gfunc bfunc pictfile
                funcfile u v transform
        0
        m A1 A2 .. Am

    """
    pass
