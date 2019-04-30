"""Radiance BSDF Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Glass
"""
import os
from .materialbase import RadianceMaterial


# TODO(): Add function file, transform and additional diffuse reflectance front and back
# and additional diffuse transmittance
class BSDF(RadianceMaterial):
    """Radiance BSDF material.

    Attributes:
        xmlfile: Path to an xml file. Data will not be cached in memory.
        up_orientation: (x, y ,z) vector that sets the hemisphere that the
            BSDF material faces.  For materials that are symmetrical about
            the HBSrf plane (like non-angled venitian blinds), this can be
            any vector that is not perfectly normal to the HBSrf. For
            asymmetrical materials like angled veneitan blinds, this variable
            should be coordinated with the direction the HBSrfs are facing.
            The default is set to (0.01, 0.01, 1.00), which should hopefully
            not be perpendicular to any typical HBSrf.
        thickness: Optional number to set the thickness of the BSDF material.
            (default: 0).
        modifier: Material modifier (Default: "void").
    """

    # TODO(): compress file content: https://stackoverflow.com/a/15529390/4394669
    # TODO(): restructure the code to include xml data and not the file.
    def __init__(self, xmlfile, name=None, up_orientation=None, thickness=None,
                 modifier="void"):
        """Create BSDF material."""
        assert os.path.isfile(xmlfile), 'Invalid path: {}'.format(xmlfile)
        assert xmlfile.lower().endswith('.xml'), 'Invalid xml file: {}'.format(xmlfile)

        self.xmlfile = os.path.normpath(xmlfile)

        name = name or '.'.join(os.path.split(self.xmlfile)[-1].split('.')[:-1])

        RadianceMaterial.__init__(self, name, modifier=modifier)

        try:
            x, y, z = up_orientation or (0.01, 0.01, 1.00)
        except TypeError as e:
            try:
                # Dynamo!
                x, y, z = up_orientation.X, up_orientation.Y, up_orientation.Z
            except AttributeError:
                # raise the original error
                raise TypeError(str(e))

        self.up_orientation = float(x), float(y), float(z)

        self.thickness = thickness or 0

        max_ln_count = 2000
        with open(self.xmlfile, 'r') as inf:
            for count, line in enumerate(inf):
                if line.strip().startswith('<IncidentDataStructure>'):
                    # get data structure
                    data_structure = line.replace('<IncidentDataStructure>', '') \
                        .replace('</IncidentDataStructure>', '').strip()
                    break
                assert count < max_ln_count, \
                    'Failed to find IncidentDataStructure in first %d lines.' \
                    % max_ln_count

        # now find the angle basis
        if data_structure.startswith('TensorTree'):
            self._angle_basis = 'TensorTree'
        elif data_structure.lower() == 'columns':
            # look for AngleBasisName
            with open(self.xmlfile, 'r') as inf:
                for i in range(count):
                    next(inf)
                for count, line in enumerate(inf):
                    if line.strip().startswith('<AngleBasisName>'):
                        self._angle_basis = line.replace('<AngleBasisName>', '') \
                            .replace('</AngleBasisName>', '').replace('LBNL/', '') \
                            .strip()
                        break
                    assert count < max_ln_count, \
                        'Failed to find AngleBasisName in first %d lines.' % max_ln_count
        else:
            raise ValueError('Unknown IncidentDataStructure: {}'.format(data_structure))

        self._update_values()

    @classmethod
    def from_file(cls, xmlfile):
        raise NotImplementedError()
        pass

    @classmethod
    def from_string(cls, material_string, modifier=None):
        """Create a Radiance material from a string.

        If the material has a modifier the modifier material should also be part of the
        string or should be provided using modifier argument.
        """

        modifier, name, base_material_data = cls._analyze_string_input(
            cls.__name__, material_string, modifier)

        assert base_material_data[8] == '0', \
            'BSDF currently does not support additional transmissions or reflections. ' \
            'You can use Custom material to create this BSDF material.'

        thickness, xmlfile, upx, upy, upz = base_material_data[1:6]

        return cls(xmlfile, name, (upx, upy, upz), thickness, modifier)

    @classmethod
    def from_json(cls, json_data):
        """Make radiance material from json.

        {
            "modifier": "", // material modifier (Default: "void")
            "type": "custom", // Material type
            "base_type": "type", // Material type
            "name": "", // Material Name
            "values": {} // values
        }
        """
        raise NotImplementedError(
            'from_json is not currently implemented for BSDF materials.')

        modifier = cls._analyze_json_input(cls.__name__.lower(), json_data)

        return cls(
            xmlfile=json_data["xml_data"],
            name=json_data["name"],
            up_orientation=json_data["up_orientation"],
            thickness=json_data["thickness"],
            modifier=modifier)

    @property
    def angle_basis(self):
        """XML file angle basis.

        Klems full, Klems half, Klems Quarter or tensor tree
        """
        return self._angle_basis

    def _update_values(self):
        "update value dictionaries."
        self._values[0] = [
            float(self.thickness),
            os.path.normpath(self.xmlfile),
            self.up_orientation[0],
            self.up_orientation[1],
            self.up_orientation[2],
            '.'
        ]

    def to_json(self):
        raise NotImplementedError(
            'to_json is not currently implemented for BSDF materials.')

        return {
            'xml_data': self.xmlfile,
            'name': self.name,
            'up_orientation': self.up_orientation,
            'thickness': self.thickness,
            'modifier': self.modifier.to_json()
        }


if __name__ == "__main__":
    # some test code
    material = BSDF(
        r".../tests/room/xmls/clear.xml")
    print(material)
