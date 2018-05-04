"""Radiance Trans2 Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Trans2
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Trans2(RadianceMaterial):
    """Radiance Trans2 Material.

    Trans2 is the anisotropic version of trans. The string arguments are the same as for
    plastic2, and the real arguments are the same as for trans but with an additional
    roughness value.

        mod trans2 id
        4+ ux uy uz funcfile transform
        0
        8 red green blue spec urough vrough trans tspec

    """
    pass
