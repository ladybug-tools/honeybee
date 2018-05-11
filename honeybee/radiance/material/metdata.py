"""Radiance Metdata Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Metdata
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Metdata(RadianceMaterial):
    """Radiance Metdata Material.

    As metfunc is to plasfunc, metdata is to plasdata. Metdata takes the same arguments
    as plasdata, but the specular component is modified by the given material color.
    """
    pass
