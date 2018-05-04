"""Radiance Plastic2 Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Plastic2
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Plastic2(RadianceMaterial):
    """Radiance Plastic2 Material.

    Plastic2 is similar to plastic, but with anisotropic roughness. This means that
    highlights in the surface will appear elliptical rather than round. The orientation
    of the anisotropy is determined by the unnormalized direction vector ux uy uz. These
    three expressions (separated by white space) are evaluated in the context of the
    function file funcfile. If no function file is required (i.e., no special variables
    or functions are required), a period (`.') may be given in its place. (See the
    discussion of Function Files in the Auxiliary Files section). The urough value
    defines the roughness along the u vector given projected onto the surface. The vrough
    value defines the roughness perpendicular to this vector. Note that the highlight
    will be narrower in the direction of the smaller roughness value. Roughness values of
    zero are not allowed for efficiency reasons since the behavior would be the same as
    regular plastic in that case.

        mod plastic2 id
        4+ ux uy uz funcfile transform
        0
        6 red green blue spec urough vrough

    """
    pass
