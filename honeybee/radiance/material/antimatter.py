"""Radiance Antimatter Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Antimatter
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Antimatter(RadianceMaterial):
    """Radiance Antimatter Material.

    Antimatter is a material that can "subtract" volumes from other volumes. A ray
    passing into an antimatter object becomes blind to all the specified modifiers:

        mod antimatter id
        N mod1 mod2 .. modN
        0
        0

    The first modifier will also be used to shade the area leaving the antimatter volume
    and entering the regular volume. If mod1 is void, the antimatter volume is completely
    invisible. Antimatter does not work properly with the material type "trans", and
    multiple antimatter surfaces should be disjoint. The viewpoint must be outside all
    volumes concerned for a correct rendering.
    """
    pass
