"""Radiance Tube.

http://radsite.lbl.gov/radiance/refer/ray.html#Tube
"""
from .geometrybase import RadianceGeometry


class Tube(RadianceGeometry):
    """Radiance Tube.
    A tube is an inverted cylinder. A cylinder is like a cone, but its starting and
    ending radii are equal.

        mod tube id
        0
        0
        7
                x0      y0      z0
                x1      y1      z1
                rad
    """
    pass
