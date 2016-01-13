class RadianceMaterialLibrary:
    # majority of methods can be modified from

    def __init__(self):
        self.loadDefaultMaterials()

    def loadDefaultMaterials(self):
        pass

    @property
    def materials(self):
        """Return list of all the available materials"""

class RadianceMaterial:
    """
    Radiance Material

    Attributes:
        name: Material name as a string
        type: Material type (e.g. glass, plastic, etc)
        modifier: Material modifier. Default is void
        values: A dictionary of material data. key is line number and item is the list of values
              {0: [], 1: [], 2: ['0.500', '0.500', '0.500', '0.000', '0.050']}
    """

    def __init__(self, name, type, values = None, modifier = "void"):
        self.name = name.rstrip()
        self.type = type.rstrip()
        self.modifier = modifier.rstrip()

        if not values: values = dict()
        self.values = values

    def toRadString(self):
        firstLine = "%s %s %s"%(self.modifier, self.type, self.name)

        material = [firstLine]
        # order is important and that's why I'm using range
        # and not the keys itself
        for lineCount in range(len(self.values.keys())):
            values = self.values[lineCount]
            count = [str(len(values))]
            line = " ".join(count + values).rstrip()
            material.append(line)
        material.append("\n")
        return "\n".join(material)

    def addValues(self, lineCount, values):
        """Add values to current material

           Args:
               lineCount: An integer that represnt the line number
               values: Values as a list of string
        """
        self.values[lineCount] = values

    def __repr__(self):
        return self.toRadString()

class RadianceGlassMaterial(RadianceMaterial):
    def __init__():
        RadianceMaterial.__init__()

    @property
    def rTransmittance(self):
        pass

    @property
    def gTransmittance(self):
        pass

    @property
    def bTransmittance(self):
        pass

    @property
    def averageTransmitance(self):
        return 0.265 * self.rTransmittance + 0.670 * self.gTransmittance + 0.065 * self.bTransmittance

    @staticmethod
    def getTransmissivity(transmittance):
            return (math.sqrt(0.8402528435 + 0.0072522239 * (transmittance ** 2)) - 0.9166530661 ) / 0.0036261119 / transmittance


class RadiancePlasticMaterial(RadianceMaterial):
    pass


class HBSurfaceRADProperties:
    def __init__(self):
        pass

    def radianceMaterial(self):
        return
