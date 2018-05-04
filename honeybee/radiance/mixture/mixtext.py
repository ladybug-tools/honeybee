"""Radiance Mixtext Mixture.

http://radsite.lbl.gov/radiance/refer/ray.html#Mixtext
"""
from .mixturebase import RadianceMixture


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Mixtext(RadianceMixture):
    """Radiance Mixtext Material.

    Mixtext uses one modifier for the text foreground, and one for the background:

        mod mixtext id
        4 foreground background fontfile textfile
        0
        9+
                Ox Oy Oz
                Rx Ry Rz
                Dx Dy Dz
                [spacing]

    or:

        mod mixtext id
        4+N
                foreground background fontfile .
                This is a line with N words ...
        0
        9+
                Ox Oy Oz
                Rx Ry Rz
                Dx Dy Dz
                [spacing]

    """
    pass
