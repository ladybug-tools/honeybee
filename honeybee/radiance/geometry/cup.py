"""Radiance Cup.

http://radsite.lbl.gov/radiance/refer/ray.html#Cup
"""
from .geometrybase import RadianceGeometry


class Cone(RadianceGeometry):
    """Radiance Cup.

    A cup is an inverted cone (i.e., has an inward surface normal).

    A cone is a megaphone-shaped object. It is truncated by two planes perpendicular to
    its axis, and one of its ends may come to a point. It is given as two axis endpoints,
    and the starting and ending radii:

        mod cone id
        0
        0
        8
                x0      y0      z0
                x1      y1      z1
                r0      r1

    """
    pass
