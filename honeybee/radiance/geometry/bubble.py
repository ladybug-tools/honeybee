"""Radiance Bubble.

http://radsite.lbl.gov/radiance/refer/ray.html#Bubble
"""
from .sphere import Sphere


class Bubble(Sphere):
    """Radiance Bubble.

    A bubble is simply a sphere whose surface normal points inward.

    mod bubble id
    0
    0
    4 xcent ycent zcent radius
    """
