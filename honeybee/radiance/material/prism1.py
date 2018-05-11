"""Radiance Prism1 Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Prism1
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Prism1(RadianceMaterial):
    """Radiance Prism1 Material.

    The prism1 material is for general light redirection from prismatic glazings,
    generating virtual light sources. It can only be used to modify a planar surface
    (i.e., a polygon or disk) and should not result in either light concentration or
    scattering. The new direction of the ray can be on either side of the material, and
    the definitions must have the correct bidirectional properties to work properly with
    virtual light sources. The arguments give the coefficient for the redirected light
    and its direction.

        mod prism1 id
        5+ coef dx dy dz funcfile transform
        0
        n A1 A2 .. An

    The new direction variables dx, dy and dz need not produce a normalized vector. For
    convenience, the variables DxA, DyA and DzA are defined as the normalized direction
    to the target light source.
    """
    pass
