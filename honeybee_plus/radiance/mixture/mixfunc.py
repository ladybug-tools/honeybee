"""Radiance Mixfunc Mixture.

http://radsite.lbl.gov/radiance/refer/ray.html#Mixfunc
"""
from .mixturebase import RadianceMixture


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Mixfunc(RadianceMixture):
    """Radiance Mixfunc Material.

    A mixfunc mixes two modifiers procedurally. It is specified as follows:

        mod mixfunc id
        4+ foreground background vname funcfile transform
        0
        n A1 A2 .. An

    Foreground and background are modifier names that must be defined earlier in the
    scene description. If one of these is a material, then the modifier of the mixfunc
    must be "void". (Either the foreground or background modifier may be "void", which
    serves as a form of opacity control when used with a material.) Vname is the
    coefficient defined in funcfile that determines the influence of foreground. The
    background coefficient is always (1-vname).
    """
    pass
