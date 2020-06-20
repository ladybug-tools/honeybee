"""Radiance Colordata Pattern.

http://radsite.lbl.gov/radiance/refer/ray.html#Colordata
"""
from .patternbase import RadiancePattern


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Colordata(RadiancePattern):
    """Radiance Colordata Pattern.

    Colordata uses an interpolated data map to modify a material's color. The map is
    n-dimensional, and is stored in three auxiliary files, one for each color. The
    coordinates used to look up and interpolate the data are defined in another auxiliary
    file. The interpolated data values are modified by functions of one or three
    variables. If the functions are of one variable, then they are passed the
    corresponding color component (red or green or blue). If the functions are of three
    variables, then they are passed the original red, green, and blue values as
    parameters.

        mod colordata id
        7+n+
                rfunc gfunc bfunc rdatafile gdatafile bdatafile
                funcfile x1 x2 .. xn transform
        0
        m A1 A2 .. Am
    """
    pass
