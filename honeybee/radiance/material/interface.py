"""Radiance Interface Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Interface
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Interface(RadianceMaterial):
    """Radiance Interface Material.

    An interface is a boundary between two dielectrics. The first transmission
    coefficient and refractive index are for the inside; the second ones are for the
    outside. Ordinary dielectrics are surrounded by a vacuum (1 1 1 1).

        mod interface id
        0
        0
        8 rtn1 gtn1 btn1 n1 rtn2 gtn2 btn2 n2

    """
    pass
