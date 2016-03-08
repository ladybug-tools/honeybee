"""Radiance Analysis Recipes."""
from abc import ABCMeta, abstractmethod
from ..sky.skyBase import RadianceSky
from ..parameters import RadianceParameters, LowQuality
from ...helper import preparedir

import os
from collections import namedtuple


class HBDaylightAnalysisRecipe(object):
    """Analysis Recipe Base class.

    Attributes:
        sky: A honeybee sky for the analysis.
        radParameters: Radiance parameters for this analysis.
            (Default: RadianceParameters.LowQuality)
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Sub-folder for this analysis recipe. (e.g. "gridbased")
    """

    __metaclass__ = ABCMeta

    def __init__(self, sky, radParameters=None, hbObjects=None, subFolder=""):
        """Create Analysis recipe."""
        self.sky = sky
        """A honeybee sky for the analysis."""

        self.radianceParameters = radParameters
        """Radiance parameters for this analysis (Default: RadianceParameters.LowQuality)."""

        self.hbObjects = hbObjects
        """An optional list of Honeybee surfaces or zones. (Default: None)"""

        self.subFolder = subFolder
        """Sub-folder for this analysis recipe. (e.g. "gridbased", "imagebased")"""

    @property
    def hbObjects(self):
        """Get and set Honeybee objects for this recipe."""
        return self.__hbObjs

    @hbObjects.setter
    def hbObjects(self, hbObjects):
        if not hbObjects:
            self.__hbObjs = []
        else:
            self.__hbObjs = [hbo for hbo in hbObjects if hasattr(hbo, 'isHBObject')]
            _dif = len(hbObjects) - len(self.__hbObjs)
            if _dif:
                print "%d non Honeybee objects are found and removed." % _dif

    @property
    def sky(self):
        """Get and set sky definition."""
        return self.__sky

    @sky.setter
    def sky(self, newSky):
        assert isinstance(newSky, RadianceSky), "%s is not a valid Honeybee sky." % type(newSky)
        self.__sky = newSky

    @property
    def radianceParameters(self, radianceParameters):
        """Get and set Radiance parameters."""
        return self.__radParameters

    @radianceParameters.setter
    def radianceParameters(self, radParameters):
        if not radParameters:
            radParameters = LowQuality()
        assert isinstance(radParameters, RadianceParameters), \
            "%s is not a radiance parameters." % type(radParameters)
        self.__radParameters = radParameters

    @property
    def subFolder(self):
        """Sub-folder for Grid-based analysis."""
        return self.__folder

    @subFolder.setter
    def subFolder(self, value):
        """Sub-folder for Grid-based analysis."""
        self.__folder = str(value)

    def hbObjectsToRadString(self):
        """Return geometries and materials as a tuple of multiline string.

        Returns:
            A namedTuple of multiline data. Keys are: materials geometries

        Usage:
            s = self.hbObjectsToRadString()
            geoString = s.geometries
            matString = s.materials
            or
            s = self.hbObjectsToRadString()
            matString, geoString = s
        """
        _radDefinition = namedtuple("RadString", "materials geometries")
        _matStr = ""
        _geoStr = ""

        if len(self.hbObjects) > 0:
            _materials = []
            _geos = []
            for hbo in self.hbObjects:
                try:
                    # hbzone or HBSurface with child surface returns a list of materials
                    _materials.extend(hbo.radianceMaterial)
                except:
                    # hb surface with no child surface
                    _materials.append(hbo.radianceMaterial)

                _geos.append(hbo.toRadString())

            # remove duplicated materials
            _materials = set([mat.toRadString() for mat in _materials])
            _matStr = "\n".join(_materials)

            # joing geometries
            _geoStr = "\n".join(_geos)

            print "Number of total materials: %d" % len(_materials)
            print "Number of total surfaces: %d" % len(_geos)
        else:
            print "Warning: Found no Honeybee objects."

        return _radDefinition(_matStr, _geoStr)

    @abstractmethod
    def toRadString(self):
        """Radiance representation of the recipe."""
        pass

    @abstractmethod
    def writeToFile(self, targetFolder):
        """Write files for the analysis recipe to file.

        Args:
            filePath: Full path for a valid file path (e.g. c:/ladybug/testPts.pts)

        Returns:
            True in case of success. False in case of failure.
        """
        pass

    # TODO: Check for white space in names. I need to test some cases to make
    # sure what will and what will not fail for Radiance before implementing this.
    @staticmethod
    def write(filePath, data, mkdir=False):
        """Write a string of data to file.

        Args:
            filePath: Full path for a valid file path (e.g. c:/ladybug/testPts.pts)
            data: Any data as string
            mkdir: Set to True to create the directory if doesn't exist (Default: False)
        """
        __dir, __name = os.path.split(filePath)

        if not os.path.isdir(__dir):
            if mkdir:
                preparedir(__dir)
            else:
                raise ValueError("Target dir doesn't exist: %s" % __dir)

        with open(filePath, "w") as outf:
            try:
                outf.write(str(data))
                return filePath
            except Exception as e:
                print "Failed to write points to file:\n%s" % e
                return False
