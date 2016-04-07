"""Radiance Custom Material (e.g plastic, glass, etc.).

Use this class to create any type of radiance materials.
http://radsite.lbl.gov/radiance/refer/ray.html#Materials
"""
from _materialbase import RadianceMaterial


class CustomMaterial(RadianceMaterial):
    """Custom Radiance material.

    Attributes:
        name: Material name as a string. Do not use white space and special character.
        materialType: One of Radiance standard Material types (e.g. glass, plastic, etc)
        values: A dictionary of material data. key is line number and item is the list of values
              {0: [], 1: [], 2: ['0.500', '0.500', '0.500', '0.000', '0.050']}
        modifier: Material modifier. Default is void

    """

    def __init__(self, name, materialType, values={}, modifier="void"):
        """Create custom radiance material."""
        RadianceMaterial.__init__(self, name, materialType, modifier="void")
        self.values = values
        """ A dictionary of material data. key is line number and item is the list of values
              {0: [], 1: [], 2: ['0.500', '0.500', '0.500', '0.000', '0.050']}
        """

    def modifyValues(self, lineCount, values):
        """Modify values for the current material.

        Args:
           lineCount: An integer between 0-2 that represnt the line number.
           values: Values as a list of string
         Usage:
            # This line will assign 9 values to line 0 of the material
            material.modifyValues(0, ["0.5", "0.5", "0.5",
                "/usr/local/lib/ray/oakfloor.pic", ".", "frac(U)",
                "frac(V)", "-s", "1.1667"])
        """
        assert 0 <= lineCount <= 2, "lineCount should be between 0-2."
        self.values[lineCount] = values

    def toRadString(self, minimal=False):
        """Return full radiance definition."""
        material = [self.headLine]

        for lineCount in xrange(3):
            try:
                values = self.values[lineCount]
            except:
                values = []  # line will be printed as 0
            else:
                count = [str(len(values))]
                line = " ".join(count + values).rstrip()
                material.append(line)

        return " ".join(material) if minimal else "\n".join(material)
