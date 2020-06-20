"""Radiance Brighttext Pattern.

http://radsite.lbl.gov/radiance/refer/ray.html#Brighttext
"""
from .patternbase import RadiancePattern


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Brighttext(RadiancePattern):
    """Radiance Brighttext Pattern.

    Brighttext is like colortext, but the writing is monochromatic.

        mod brighttext id
        2 fontfile textfile
        0
        11+
                Ox Oy Oz
                Rx Ry Rz
                Dx Dy Dz
                foreground background
                [spacing]

    or:

        mod brighttext id
        2+N fontfile . This is a line with N words ...
        0
        11+
                Ox Oy Oz
                Rx Ry Rz
                Dx Dy Dz
                foreground background
                [spacing]

    By default, a uniform spacing algorithm is used that guarantees every character will
    appear in a precisely determined position. Unfortunately, such a scheme results in
    rather unattractive and difficult to read text with most fonts. The optional spacing
    value defines the distance between characters for proportional spacing. A positive
    value selects a spacing algorithm that preserves right margins and indentation, but
    does not provide the ultimate in proportionally spaced text. A negative value insures
    that characters are properly spaced, but the placement of words then varies
    unpredictably. The choice depends on the relative importance of spacing versus
    formatting. When presenting a section of formatted text, a positive spacing value is
    usually preferred. A single line of text will often be accompanied by a negative
    spacing value. A section of text meant to depict a picture, perhaps using a special
    purpose font such as hexbit4x1.fnt, calls for uniform spacing. Reasonable magnitudes
    for proportional spacing are between 0.1 (for tightly spaced characters) and 0.3 (for
    wide spacing).
    """
    pass
