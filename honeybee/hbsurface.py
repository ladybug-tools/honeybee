from abc import ABCMeta, abstractmethod, abstractproperty

# TODO: Finish the implementation!
class Surface:
    """Minimum implementation of base Honeybee surface"""
    __metaclass__ = ABCMeta

    def __init__(self, name, isNameSetByUser = False, EPProperties = None, RADProperties = None):
        self.name(name, isNameSetByUser)

    @property
    def name(self):
        "surface name"
        return self.__name

    @name.setter
    def name(self, newName, isSetByUser = False):
        # name should be checked not to have illegal charecters for ep and radiance
        self.__name = newName
        self.__isNameSetByUser = isSetByUser

    def isNameSetByUser(self):
        return self.__isNameSetByUser

    @abstractproperty
    def geometry(self):
        "It needs to be implemented in geometry libraries"
        pass

    @abstractmethod
    def getEnergyPlusDefinition(self, includeConstruction = False, includeMaterials = False):
        """Return EnergyPlus definition for this surface"""
        pass

    @abstractmethod
    def getRadianceDefinition(self, includeMaterial = False):
        pass

    def getEnergyPlusConstruction(self):
        """Return surface EnergyPlus construction"""
        pass

    def getEnergyPlusMaterials(self, layerNumber = None):
        """Return list of EnergyPlus materials for this surface"""
        pass




class HBSurface(Surface):
    """Minimum implementation of Honeybee surface"""

    def __init__(self):
        pass

    @property
    def geometry(self):
        """return geometry"""
        return self.__geometry

    @geometry.setter
    def geometry(self, geo):
        """set geometry"""
        self.__geometry = geo
