"""Radiance Texdata Texture.

A texture is a perturbation of the surface normal, and is given by either a function or
data.

http://radsite.lbl.gov/radiance/refer/ray.html#Texdata
"""
from .texturebase import RadianceTexture


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Texdata(RadianceTexture):
    """Radiance Texdata Material.

    A texdata texture uses three data files to get the surface normal perturbations. The
    variables xfunc, yfunc and zfunc take three arguments each from the interpolated
    values in xdfname, ydfname and zdfname.

        mod texdata id
        8+ xfunc yfunc zfunc xdfname ydfname zdfname vfname x0 x1 .. xf
        0
        n A1 A2 .. An

    """
    pass
