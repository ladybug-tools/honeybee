"""Radiance Plasfunc Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Plasfunc
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Plasfunc(RadianceMaterial):
    """Radiance Plasfunc Material.

    Plasfunc in used for the procedural definition of plastic-like materials with
    arbitrary bidirectional reflectance distribution functions (BRDF's). The arguments
    to this material include the color and specularity, as well as the function defining
    the specular distribution and the auxiliary file where it may be found.

            mod plasfunc id
            2+ refl funcfile transform
            0
            4+ red green blue spec A5 ..

    The function refl takes four arguments, the x, y and z direction towards the incident
    light, and the solid angle subtended by the source. The solid angle is provided to
    facilitate averaging, and is usually ignored. The refl function should integrate to
    1 over the projected hemisphere to maintain energy balance. At least four real
    arguments must be given, and these are made available along with any additional
    values to the reflectance function. Currently, only the contribution from direct
    light sources is considered in the specular calculation. As in most material types,
    the surface normal is always altered to face the incoming ray. 
    """
    pass
