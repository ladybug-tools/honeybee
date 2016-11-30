"""Base ckass for RADIANCE Analysis Recipes."""
from abc import ABCMeta, abstractmethod
from ...helper import preparedir, writeToFile, copyFilesToFolder

from collections import namedtuple
import os
import subprocess


class HBDaylightAnalysisRecipe(object):
    """Analysis Recipe Base class.

    Attributes:
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Sub-folder for this analysis recipe. (e.g. "gridbased")
    """

    __metaclass__ = ABCMeta

    def __init__(self, hbObjects=None, subFolder=None):
        """Create Analysis recipe."""
        self.hbObjects = hbObjects
        """An optional list of Honeybee surfaces or zones. (Default: None)"""

        self.subFolder = subFolder
        """Sub-folder for this analysis recipe. (e.g. "gridbased", "imagebased")"""

        self.additionalRadianceFiles = []
        """Additional Radiance files other than honeybee objects.

            Thes files will be added to the radiance scene. If you're adding files
            that are dependant on each other they should be in the correct order.

            Valid files are *.rad, *.mat and *.oct.
        """
        self.copyAdditionalFilesLocally = True
        """A boolean that indicates to copy additional files to the radiance folder.
            (default: True)
        """
        self.resultsFile = []
        self.commands = []
        self.isCalculated = False
        self.isChanged = True

    @property
    def isAnalysisRecipe(self):
        """Return true to indicate it is an analysis recipe."""
        return True

    @property
    def hbObjects(self):
        """Get and set Honeybee objects for this recipe."""
        return self.__hbObjs

    @hbObjects.setter
    def hbObjects(self, hbObjects):
        if not hbObjects:
            self.__hbObjs = ()
            self.__radianceMaterials = ()
        else:
            try:
                self.__radianceMaterials = \
                    set(mat for hbo in hbObjects for mat in hbo.radianceMaterials)
            except AttributeError:
                raise TypeError('At the minimum one of the inputs is not a Honeybee object.')

            self.__hbObjs = hbObjects

    @property
    def radianceMaterials(self):
        """Get list of radiance materials for Honeybee objects in this recipe."""
        return self.__radianceMaterials

    @property
    def subFolder(self):
        """Sub-folder for Grid-based analysis."""
        return self.__subFolder

    @subFolder.setter
    def subFolder(self, value):
        """Sub-folder for Grid-based analysis."""
        self.__subFolder = str(value)

    @property
    def additionalRadianceFiles(self):
        """Additional Radiance files other than honeybee objects.

        Thes files will be added to the radiance scene. If you're adding files
        that are dependant on each other they should be in the correct order.

        Valid files are *.rad, *.mat and *.oct.
        """
        return self.__additionalRadianceFiles

    @additionalRadianceFiles.setter
    def additionalRadianceFiles(self, arf):
        if not arf:
            self.__additionalRadianceFiles = ()
        else:
            _f = namedtuple('AdditionalRadianceFiles', 'mat rad oct')
            self.__additionalRadianceFiles = _f(
                tuple(f for f in arf if arf.lower().endswith('.mat')),
                tuple(f for f in arf if arf.lower().endswith('.rad')),
                tuple(f for f in arf if arf.lower().endswith('.oct')))

    def prepareSubFolder(self, targetFolder,
                         subFolders=('.tmp', 'objects', 'skies', 'results'),
                         removeContent=True):
        """Create subfolders under targetFolder/self.subfolder.

        By default a honeybee radiance analysis folder structure is as below.
        . taragetFolder
            .. subfolder
                . command.bat
                . *.pts  # point files
                . *.vf  # view files
                . *.oct  # octree files
                .. .tmp (*.tmp)  # This folder will be removed after running the analysis
                .. objects (*.rad, *.mat)
                .. skies (*.sky, *.wea)
                .. results
                    ..matrix (*.vmx, *.dmx) # only for 3-Phase analysis
                    ..hdr (*.hdr)  # only for view-based analysis
                    ..ill (*.ill)  # illuminance values for annual analysis
        """
        for f in subFolders:
            p = os.path.join(targetFolder, self.subFolder, f)
            preparedir(p, removeContent)

    def toRadStringGeometries(self):
        """Return geometries radiance definition as a single multiline string."""
        print 'Number of Honeybee objects: %d' % len(self.hbObjects)
        _geos = (hbo.toRadString(includeMaterials=False, joinOutput=True)
                 for hbo in self.hbObjects)

        return "\n".join(_geos)

    def toRadStringMaterials(self):
        """Return radiance definition of materials as a single multiline string."""
        print 'Number of radiance materials: %d' % len(self.radianceMaterials)
        return "\n".join((hbo.toRadString() for hbo in self.radianceMaterials))

    def toRadStringMaterialsAndGeometries(self):
        """Return geometries radiance definition as a single multiline string."""
        _mattgeos = (hbo.toRadString(includeMaterials=True, joinOutput=True)
                     for hbo in self.hbObjects)

        return "\n".join(_mattgeos)

    # TODO: Get commands without running write method.
    def toRadString(self):
        """Radiance representation of the recipe."""
        return '\n'.join(self.commands)

    def writeGeometriesToFile(self, targetDir, fileName, mkdir=False):
        """Write geometries to file.

        Args:
            targetDir: Path to project directory (e.g. c:/ladybug)
            fileName: File name as string. materials will be saved as
                fileName.rad

        Returns:
            Path to file in case of success.

        Exceptions:
            ValueError if targetDir doesn't exist and mkdir is False.
        """
        assert type(fileName) is str, 'fileName should be a string.'
        fileName = fileName if fileName.lower().endswith('.rad') \
            else fileName + '.rad'

        return writeToFile(os.path.join(targetDir, fileName),
                           self.toRadStringGeometries() + "\n", mkdir)

    def writeMatrialsToFile(self, targetDir, fileName, mkdir=False):
        """Write materials to file.

        Args:
            targetDir: Path to project directory (e.g. c:/ladybug)
            fileName: File name as string. materials will be saved as
                fileName.mat

        Returns:
            Path to file in case of success.

        Exceptions:
            ValueError if targetDir doesn't exist and mkdir is False.
        """
        assert type(fileName) is str, 'fileName should be a string.'
        fileName = fileName if fileName.lower().endswith('.mat') \
            else fileName + '.mat'

        return writeToFile(os.path.join(targetDir, fileName),
                           self.toRadStringMaterials() + "\n", mkdir)

    def writeMaterialsAndGeometriesToFile(self, targetDir, fileName, mkdir=False):
        """Write geometries to file.

        Args:
            targetDir: Path to project directory (e.g. c:/ladybug)
            fileName: File name as string. materials will be saved as
                fileName.rad

        Returns:
            Path to file in case of success.

        Exceptions:
            ValueError if targetDir doesn't exist and mkdir is False.
        """
        assert type(fileName) is str, 'fileName should be a string.'
        fileName = fileName if fileName.lower().endswith('.rad') \
            else fileName + '.rad'

        return writeToFile(os.path.join(targetDir, fileName),
                           self.toRadStringMaterialsAndGeometries() + "\n",
                           mkdir)

    def write(self, targetFolder, projectName='untitled', relPath=True):
        """Write geometry and material files to folder.

        Returns:
            studyFolder, Materil files, geometry files, octree files
        """
        if not targetFolder:
            targetFolder = os.path.join(os.environ['USERPROFILE'], 'honeybee')

        _ispath = preparedir(targetFolder, False)
        assert _ispath, "Failed to create %s. Try a different path!" % targetFolder

        projectName = 'untitled' if not projectName else str(projectName)

        _basePath = os.path.join(targetFolder, projectName)
        _ispath = preparedir(_basePath, removeContent=False)
        assert _ispath, "Failed to create %s. Try a different path!" % _basePath

        # create subfolders inside the folder
        self.prepareSubFolder(_basePath,
                              subFolders=('objects', 'skies', 'results'),
                              removeContent=True)

        _path = os.path.join(_basePath, self.subFolder)
        # Check if anything has changed
        # if not self.isChanged:
        #     print "Inputs has not changed! Check files at %s" % _path

        # 3.write materials and geometry files
        matFile = self.writeMatrialsToFile(_path + '/objects', projectName)
        geoFile = self.writeGeometriesToFile(_path + '/objects', projectName)

        # 3.1. copy additional files if anything
        if self.additionalRadianceFiles and self.copyAdditionalFilesLocally:
            matFilesAdd = copyFilesToFolder(self.additionalRadianceFiles.mat,
                                            _path + '/objects')
            radFilesAdd = copyFilesToFolder(self.additionalRadianceFiles.rad,
                                            _path + '/objects')
            octFilesAdd = copyFilesToFolder(self.additionalRadianceFiles.oct,
                                            _path + '/objects')
        elif self.additionalRadianceFiles:
            matFilesAdd = self.additionalRadianceFiles.mat
            radFilesAdd = self.additionalRadianceFiles.rad
            octFilesAdd = self.additionalRadianceFiles.oct
        else:
            matFilesAdd, radFilesAdd, octFilesAdd = [], [], []

        files = namedtuple(
            'Files', 'path geoFile matFile radFilesAdd matFilesAdd octFilesAdd'
        )

        return files(_path, geoFile, matFile, radFilesAdd, matFilesAdd,
                     octFilesAdd)

    # TODO: Write a runmanager class to handle runs
    def run(self, commandFile, debug=False):
        """Run the analysis."""
        assert os.path.isfile(commandFile), \
            ValueError('Failed to find command file: {}'.format(commandFile))

        if debug:
            with open(self.__batchFile, "a") as bf:
                bf.write("\npause\n")

        subprocess.call(commandFile)

        self.isCalculated = True
        # self.isChanged = False
        return True

    @abstractmethod
    def results(self):
        """Return results for this analysis."""
        pass

    @staticmethod
    def relpath(path, start):
        """Return a relative path."""
        return os.path.relpath(path, start)
