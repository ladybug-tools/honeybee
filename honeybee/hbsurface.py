from abc import ABCMeta, abstractmethod, abstractproperty


# TODO: Add points property.
# Analysis surface should work without geometry and based on points Input
# In this approach we can implement all the methods in honeybee-core and test
# them with no need to geometries. Also down the road I can see people use this
# library just for creating idf files and so on
class AnalysisSurface(object):
    """Base class for Honeybee surface.

    WARNING: Do NOT use this class directly.
    """

    __metaclass__ = ABCMeta

    def __init__(self, name, isNameSetByUser=False, EPProperties=None, RADProperties=None):
        """Initialize Honeybee Surface."""
        self.name = (name, isNameSetByUser)

    @property
    def name(self):
        """Retuen surface name."""
        return self.__name

    # TODO: name should be checked not to have illegal charecters for ep and radiance
    @name.setter
    def name(self, values):
        """Set name and isSetByUser property.

        Args:
            values: A name or a tuple as (name, isSetByUser)

        Usage:
            HBSrf.name = "surface_001"
            # or
            HBSrf.name = ("mySurfaceName", True)
        """
        try:
            # check if user passed a tuple
            __newName, __isNameSetByUser = values
        except ValueError:
            # user is passing a list or tuple with one ValueError
            __newName = values[0]
            __isNameSetByUser = False  # if not indicated assume it is not set by user.
        except TypeError:
            # user just passed a single value which is the name
            __newName = values
            __isNameSetByUser = False  # if not indicated assume it is not set by user.
        finally:
            # set new name
            self.__name = str(__newName)
            self.__isNameSetByUser = __isNameSetByUser

    def isNameSetByUser(self):
        """Return if name is set by user.

        If name is set by user the surface will never be named automatically.
        """
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
        # calculate center point and normal

        # calculate surface baseplane
