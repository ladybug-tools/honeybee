"""Radiance Ashik2 Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Ashik2
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Ashik2(RadianceMaterial):
    """Radiance Ashik2 Material.

    Ashik2 is the anisotropic reflectance model by Ashikhmin & Shirley. The string
    arguments are the same as for plastic2, but the real arguments have additional
    flexibility to specify the specular color. Also, rather than roughness, specular
    power is used, which has no physical meaning other than larger numbers are equivalent
    to a smoother surface.

        mod ashik2 id
        4+ ux uy uz funcfile transform
        0
        8 dred dgrn dblu sred sgrn sblu u-power v-power
    """
    pass
