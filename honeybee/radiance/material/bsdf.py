"""Radiance BSDF Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Glass
"""
import os
from _materialbase import RadianceMaterial


class BSDFMaterial(RadianceMaterial):
    """Radiance BSDF material.

    Attributes:
        xmlfile: Path to an xml file. Data will not be cached in memory.
        upOrientation: (x, y ,z) vector that sets the hemisphere that the
            BSDF material faces.  For materials that are symmetrical about
            the HBSrf plane (like non-angled venitian blinds), this can be
            any vector that is not perfectly normal to the HBSrf. For
            asymmetrical materials like angled veneitan blinds, this variable
            should be coordinated with the direction the HBSrfs are facing.
            The default is set to (0.01, 0.01, 1.00), which should hopefully
            not be perpendicular to any typical HBSrf.
        thickness: Optional number to set the thickness of the BSDF material.
            (default: 0)
        modifier: Material modifier (Default: "void").
    """

    def __init__(self, xmlfile, upOrientation=None, thickness=None, modifier="void"):
        """Create BSDF material."""
        assert os.path.isfile(xmlfile), 'Invalid path: {}'.format(xmlfile)
        assert xmlfile.lower().endswith('.xml'), 'Invalid xml file: {}'.format(xmlfile)

        self.xmlfile = os.path.normpath(xmlfile)

        name = '.'.join(os.path.split(self.xmlfile)[-1].split('.')[:-1])

        RadianceMaterial.__init__(self, name, materialType="BSDF", modifier=modifier)
        try:
            x, y, z = upOrientation or (0.01, 0.01, 1.00)
        except TypeError as e:
            try:
                # Dynamo!
                x, y, z = upOrientation.X, upOrientation.Y, upOrientation.Z
            except AttributeError:
                # raise the original error
                raise TypeError(str(e))

        self.upOrientation = x, y, z
        self.thickness = thickness or 0

    @property
    def isGlassMaterial(self):
        """Indicate if this object has glass Material.

        This property will be used to separate the glass surfaces in a separate
        file than the opaque surfaces.
        """
        return True

    def toRadString(self, minimal=False):
        """Return full radiance definition."""
        baseString = self.headLine + "6 %.3f %s %.3f %.3f %.3f .\n0\n0\n"

        matDef = baseString % (self.thickness,
                               os.path.normpath(self.xmlfile),
                               self.upOrientation[0],
                               self.upOrientation[1],
                               self.upOrientation[2])

        return matDef.replace("\n", " ") if minimal else matDef


if __name__ == "__main__":
    # some test code
    material = BSDFMaterial(
        r"C:\Users\Administrator\Documents\GitHub\honeybee\tests\room\xmls\clear.xml")
    print material
