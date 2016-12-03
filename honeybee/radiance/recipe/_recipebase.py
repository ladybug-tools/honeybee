"""Base ckass for RADIANCE Analysis Recipes."""
from ...helper import preparedir, writeToFile, copyFilesToFolder, \
    getRadiancePathLines

from collections import namedtuple
import os
import subprocess


class DaylightAnalysisRecipe(object):
    """Analysis Recipe Base class.

    Attributes:
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Sub-folder for this analysis recipe. (e.g. "gridbased")
    """

    def __init__(self, hbObjects=None, subFolder=None, scene=None):
        """Create Analysis recipe."""
        self.hbObjects = hbObjects
        """An optional list of Honeybee surfaces or zones. (Default: None)"""

        self.subFolder = subFolder
        """Sub-folder for this analysis recipe. (e.g. "gridbased", "imagebased")"""

        self.scene = scene
        """Additional Radiance files other than honeybee objects."""

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
    def scene(self):
        """A base scene for the recipe."""
        return self.__scene

    @scene.setter
    def scene(self, sc):
        if not sc:
            self.__scene = None
        else:
            assert hasattr(sc, 'files'), '{} is not a Radiance Scene. ' \
                'Scene should be an instance from the type Scene.'.format(sc)
            self.__scene = sc

    # TODO: This should be cross platform and also support cloud-based modeling.
    def header(self, targetFolder, includRadPath=True):
        """Get the header for bat file."""
        dirLine = "%s\ncd %s\n" % (os.path.splitdrive(targetFolder)[0], targetFolder)

        if includRadPath:
            return '\n'.join((getRadiancePathLines(), dirLine))
        else:
            return dirLine

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
        _mat = self.toRadStringMaterials()
        _geo = self.toRadStringGeometries()

        return "\n".join((_mat, _geo))

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

    def write(self, targetFolder, projectName='untitled',
              subFolders=('objects', 'skies', 'results'),
              removeSubFoldersContent=True):
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

        print 'Preparing %s' % os.path.join(_basePath, self.subFolder)
        # create subfolders inside the folder
        self.prepareSubFolder(_basePath,
                              subFolders=subFolders,
                              removeContent=removeSubFoldersContent)

        if self.scene:
            self.prepareSubFolder(_basePath, subFolders=('scene',),
                                  removeContent=self.scene.overwrite)

        _path = os.path.join(_basePath, self.subFolder)
        # Check if anything has changed
        # if not self.isChanged:
        #     print "Inputs has not changed! Check files at %s" % _path

        # 3.write materials and geometry files
        matFile = self.writeMatrialsToFile(_path + '\\objects', projectName)
        geoFile = self.writeGeometriesToFile(_path + '\\objects', projectName)

        # 3.1. copy scene files if anything
        if self.scene:
            if self.scene.numberOfFiles == 1:
                print 'Adding one file from the radiance scene.'
            else:
                print 'Adding %d files from the radiance scene.' % \
                    self.scene.numberOfFiles

            if self.scene.copyLocal:
                matFilesAdd = copyFilesToFolder(
                    self.scene.files.mat, _path + '\\scene', self.scene.overwrite)
                radFilesAdd = copyFilesToFolder(
                    self.scene.files.rad, _path + '\\scene', self.scene.overwrite)
                octFilesAdd = copyFilesToFolder(
                    self.scene.files.oct, _path + '\\scene', self.scene.overwrite)
            else:
                matFilesAdd = self.scene.files.mat
                radFilesAdd = self.scene.files.rad
                octFilesAdd = self.scene.files.oct
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
            with open(commandFile, "a") as bf:
                bf.write("\npause\n")

        subprocess.call(commandFile)

        self.isCalculated = True
        # self.isChanged = False
        return True

    def results(self):
        """Return results for this analysis."""
        raise NotImplementedError()

    @staticmethod
    def relpath(path, start):
        """Return a relative path."""
        return os.path.relpath(path, start)
