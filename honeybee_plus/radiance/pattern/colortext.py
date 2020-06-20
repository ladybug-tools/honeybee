"""Radiance Colortext Pattern.

http://radsite.lbl.gov/radiance/refer/ray.html#Colortext
"""
from .patternbase import RadiancePattern


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Colortext(RadiancePattern):
    """Radiance Colortext Pattern.

    Colortext is dichromatic writing in a polygonal font. The font is defined in an
    auxiliary file, such as helvet.fnt. The text itself is also specified in a separate
    file, or can be part of the material arguments. The character size, orientation,
    aspect ratio and slant is determined by right and down motion vectors. The upper left
    origin for the text block as well as the foreground and background colors must also
    be given.

        mod colortext id
        2 fontfile textfile
        0
        15+
                Ox Oy Oz
                Rx Ry Rz
                Dx Dy Dz
                rfore gfore bfore
                rback gback bback
                [spacing]

or:

        mod colortext id
        2+N fontfile . This is a line with N words ...
        0
        15+
                Ox Oy Oz
                Rx Ry Rz
                Dx Dy Dz
                rfore gfore bfore
                rback gback bback
                [spacing]

    """
    pass
