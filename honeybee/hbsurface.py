from abc import ABCMeta, abstractmethod, abstractproperty


# TODO: Finish the implementation!
class AnalysisSurface(object):
    """Minimum implementation of base Honeybee surface."""

    __metaclass__ = ABCMeta

    def __init__(self, name, isNameSetByUser=False, EPProperties=None, RADProperties=None):
        """Initialize Honeybee Surface."""
        self.name = name

    @property
    def name(self):
        """Retuen surface name."""
        return self.__name

    @name.setter
    def name(self, newName, isSetByUser=False):
        # name should be checked not to have illegal charecters for ep and radiance
        self.__name = newName
        self.__isNameSetByUser = isSetByUser

    def isNameSetByUser(self):
        """Check if name is set by user."""
        return self.__isNameSetByUser

    @abstractproperty
    def geometry(self):
        """Set and return geometry.

        It needs to be implemented in geometry libraries
        """
        pass

    @abstractmethod
    def getEnergyPlusDefinition(self, includeConstruction=False, includeMaterials=False):
        """Return EnergyPlus definition for this surface."""
        pass

    @abstractmethod
    def getRadianceDefinition(self, includeMaterial=False):
        """Return Radiance definition for this surface."""
        pass

    def getEnergyPlusConstruction(self):
        """Return surface EnergyPlus construction."""
        pass

    def getEnergyPlusMaterials(self, layerNumber=None):
        """Return list of EnergyPlus materials for this surface."""
        pass


class HBSurface(AnalysisSurface):
    """Minimum implementation of Honeybee surface."""

    def __init__(self):
        """Initialize Honeybee Surface."""
        pass

    @property
    def geometry(self):
        """return geometry."""
        return self.__geometry

    @geometry.setter
    def geometry(self, geo):
        """Set geometry."""
        self.__geometry = geo
