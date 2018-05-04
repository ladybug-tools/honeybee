"""Radiance Texfunc Texture.

A texture is a perturbation of the surface normal, and is given by either a function or
data.

http://radsite.lbl.gov/radiance/refer/ray.html#Texfunc
"""
from .texturebase import RadianceTexture


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Texfunc(RadianceTexture):
    """Radiance Texfunc Material.

    A texfunc uses an auxiliary function file to specify a procedural texture:

        mod texfunc id
        4+ xpert ypert zpert funcfile transform
        0
        n A1 A2 .. An
    """
    pass
