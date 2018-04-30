"""Radiance generic material."""
from .materialbase import RadianceMaterial


class Custom(RadianceMaterial):
    """Custom Radiance material.

    Attributes:
        name: Primitive name as a string. Do not use white space and special character.
        type: One of Radiance standard Primitive types (e.g. glass, plastic, etc)
        values: A dictionary of primitive data. key is line number and item is the list
            of values {0: [], 1: [], 2: ['0.500', '0.500', '0.500', '0.000', '0.050']}
        modifier: Modifier. It can be material, mixture, texture or pattern. Honeybee
            currently only supports materials. For other types use Generic primitive
            class (Default: "void").
    """

    def __init__(self, name, type, values, modifier=None):
        """Create custom radiance material."""
        RadianceMaterial.__init__(self, name, type, modifier=modifier)
        self.values = values
        """ A dictionary of material data. key is line number and item is the list of
            values {0: [], 1: [], 2: ['0.500', '0.500', '0.500', '0.000', '0.050']}
        """
        self._isGlassMaterial = False

    @classmethod
    def from_string(cls, material_string, modifier=None):
        """Create a Radiance material from a string.

        If the material has a modifier the modifier material should also be part of the
        string or should be provided using modifier argument.
        """
        material_type = cls._get_string_type(material_string)

        modifier, name, base_data = cls._analyze_string_input(
            None, material_string, modifier)

        count_1 = int(base_data[0])
        count_2 = int(base_data[count_1 + 1])
        count_3 = int(base_data[count_1 + count_2 + 2])

        l1 = [] if count_1 == 0 else base_data[1: count_1 + 1]
        l2 = [] if count_2 == 0 \
            else base_data[count_1 + 2: count_1 + count_2 + 2]
        l3 = [] if count_3 == 0 \
            else base_data[count_1 + count_2 + 3: count_1 + count_2 + count_3 + 3]

        values = {0: l1, 1: l2, 2: l3}

        return cls(name, material_type, values, modifier)

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, new_values):
        """Modify values for the current material.

        Args:
           new_values: New values as a dictionary. The keys should be between 0 and 2.

         Usage:
            # This line will assign 9 values to line 0 of the material
            material.values = {0: ["0.5", "0.5", "0.5",
                "/usr/local/lib/ray/oakfloor.pic", ".", "frac(U)",
                "frac(V)", "-s", "1.1667"]}
        """
        self._values = {}
        for line_count, value in new_values.iteritems():
            assert 0 <= line_count <= 2, ValueError(
                'Illegal input: {}. Key values must be between 0-2.'.format(line_count)
            )
            self._values[line_count] = value

    @property
    def isGlassMaterial(self):
        """Indicate if this object has glass Material.

        This property will be used to separate the glass surfaces in a separate
        file than the opaque surfaces.
        """
        return self._isGlassMaterial

    @isGlassMaterial.setter
    def isGlassMaterial(self, input):
        """Set if this material is transparent.

        This property will be used to separate the glass surfaces in a separate
        file than the opaque surfaces.
        """
        self._isGlassMaterial = input  # expose is glass material

    def to_rad_string(self, minimal=False):
        """Return full radiance definition."""
        output = [self.head_line(minimal).strip()]

        for line_count in xrange(3):
            try:
                values = self.values[line_count]
            except BaseException:
                values = []  # line will be printed as 0
            else:
                count = [str(len(values))]
                line = " ".join(count + values).rstrip()
                output.append(line)

        return " ".join(output) if minimal else "\n".join(output)
