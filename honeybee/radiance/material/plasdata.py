"""Radiance Plasdata Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Plasdata
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Plasdata(RadianceMaterial):
    """Radiance Plasdata Material.

    Plasdata is used for arbitrary BRDF's that are most conveniently given as
    interpolated data. The arguments to this material are the data file and coordinate
    index functions, as well as a function to optionally modify the data values.

        mod plasdata id
        3+n+
                func datafile
                funcfile x1 x2 .. xn transform
        0
        4+ red green blue spec A5 ..

    The coordinate indices (x1, x2, etc.) are themselves functions of the x, y and z
    direction to the incident light, plus the solid angle subtended by the light source
    (usually ignored). The data function (func) takes five variables, the interpolated
    value from the n-dimensional data file, followed by the x, y and z direction to the
    incident light and the solid angle of the source. The light source direction and
    size may of course be ignored by the function.
    """
    pass
