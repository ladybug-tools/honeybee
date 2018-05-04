"""Radiance Dielectric Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Dielectric
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Dielectric(RadianceMaterial):
    """Radiance Dielectric Material.

    A dielectric material is transparent, and it refracts light as well as reflecting it.
    Its behavior is determined by the index of refraction and transmission coefficient in
    each wavelength band per unit length. Common glass has a index of refraction (n)
    around 1.5, and a transmission coefficient of roughly 0.92 over an inch. An
    additional number, the Hartmann constant, describes how the index of refraction
    changes as a function of wavelength. It is usually zero. (A pattern modifies only the
    refracted value.)

        mod dielectric id
        0
        0
        5 rtn gtn btn n hc

    """
    pass
