"""Base class for RADIANCE Analysis Recipes."""
from ...futil import preparedir, getRadiancePathLines
from .recipeutil import inputSrfsToRadFiles

import os
import subprocess


class AnalysisRecipe(object):
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

        self._radFile = None
        self._hbObjs = ()
        self._radianceMaterials = ()
        self._commands = []
        self._resultFiles = []
        self._isCalculated = False
        self.isChanged = True

    @classmethod
    def fromJson(cls):
        """Create analysis grid from json object."""
        raise NotImplementedError(
            "fromJson is not implemented for {}.".format(cls.__class__.__name__)
        )

    @property
    def isAnalysisRecipe(self):
        """Return true to indicate it is an analysis recipe."""
        return True

    @property
    def isCalculated(self):
        """Return True if the recipe is calculated."""
        return self._isCalculated

    @property
    def resultFiles(self):
        """Get list of result files for this recipe."""
        return self._resultFiles

    @property
    def commands(self):
        """List of recipe commands."""
        return self._commands

    @property
    def hbObjects(self):
        """Get and set Honeybee objects for this recipe."""
        return self._hbObjs

    @hbObjects.setter
    def hbObjects(self, hbObjects):
        if not hbObjects:
            self._hbObjs = ()
            self._opaque = None
            self._glazing = None
            self._wgs = ()
        else:
            self._hbObjs = []
            try:
                for obj in hbObjects:
                    if hasattr(obj, 'isHBZone'):
                        self._hbObjs.extend(obj.surfaces)
                        for srf in obj.surfaces:
                            self._hbObjs.extend(srf.childrenSurfaces)
                    elif obj.isHBAnalysisSurface:
                        self._hbObjs.append(obj)
                        try:
                            self._hbObjs.extend(obj.childrenSurfaces)
                        except AttributeError:
                            # HBFenSurfaces
                            pass
            except AttributeError as e:
                raise TypeError(
                    'Object inputs must be Honeybee Zones or Surfaces:\n{}'.format(e)
                )

        self._opaque, self._glazing, self._wgs = inputSrfsToRadFiles(self._hbObjs)

    @property
    def opaqueSurfaces(self):
        """Collection of opaque surfaces in this recipe."""
        return self._opaque.hbSurfaces

    @property
    def glazingSurfaces(self):
        """Collection of glazing surfaces in this recipe."""
        return self._glazing.hbSurfaces

    @property
    def windowGroups(self):
        """Collection of window groups in this recipe."""
        return tuple(wg.hbSurfaces[0] for wg in self._wgs)

    @property
    def opaqueRadFile(self):
        """A RadFile for opaque surfaces in this recipe."""
        return self._opaque

    @property
    def glazingRadFile(self):
        """A RadFile for glazing surfaces in this recipe."""
        return self._glazing

    @property
    def windowGroupsRadFiles(self):
        """Collection of RadFiles for window groups in this recipe."""
        return self._wgs

    @property
    def subFolder(self):
        """Sub-folder for Grid-based analysis."""
        return self._subFolder

    @subFolder.setter
    def subFolder(self, value):
        """Sub-folder for Grid-based analysis."""
        self._subFolder = str(value)

    @property
    def scene(self):
        """A base honeybee.radiance.scene for the recipe."""
        return self._scene

    @scene.setter
    def scene(self, sc):
        if not sc:
            self._scene = None
        else:
            assert hasattr(sc, 'files'), '{} is not a Radiance Scene. ' \
                'Scene should be an instance from the type Scene.'.format(sc)
            self._scene = sc

    def header(self, targetFolder, includRadPath=True):
        """Get the header for bat file.

        The header changes the path into project path and also add lines to set PATH and
        PATHRAY for Radiance.

        IncludeRadPath is only useful for Windows.

        Args:
            targetFolder: Full path to working directory.
            includRadPath: At the Boolean to True to include path to radiance
                installation folder.
        """
        dirLine = "%s\ncd %s\n" % (os.path.splitdrive(targetFolder)[0], targetFolder)

        if includRadPath:
            return '\n'.join((getRadiancePathLines(), dirLine))
        else:
            return dirLine

    # TODO: Get commands without running write method.
    def toRadString(self):
        """Radiance representation of the recipe."""
        assert len(self.commands) != 0, \
            Exception('You must write the recipe to get the list of commands'
                      ' as radString.')
        return '\n'.join(self.commands)

    def writeContent(self, targetFolder, projectName='untitled', removeContent=True,
                     subfolders=[]):
        """Write geometry and material files to folder for this recipe.

        This method in recipebase creates the folder and subfolders for 'scene',
        'result' and 'sky' which is shared between all the recipes. If there is a
        scene added to the recipe by user a folder will be created as 'scene/extra'.

        Args:
            subfolders: List of subfolders to be added to 'scene', 'sky' and 'result'.
        Returns:
            Path to analysis folder.
        """
        self._commands = []
        self._resultFiles = []

        if not targetFolder:
            targetFolder = os.path.join(os.environ['USERPROFILE'], 'honeybee')

        iscreated = preparedir(targetFolder, False)
        assert iscreated, "Failed to create %s. Try a different path!" % targetFolder

        projectName = projectName or 'untitled'

        _basePath = os.path.join(targetFolder, projectName, self.subFolder)
        iscreated = preparedir(_basePath, removeContent=False)
        assert iscreated, "Failed to create %s. Try a different path!" % _basePath

        print 'Writing recipe contents to: %s' % _basePath

        # create subfolders inside the folder
        subfolders += ['scene', 'sky', 'result']
        for folder in subfolders:
            ff = os.path.join(_basePath, folder)
            iscreated = preparedir(ff, removeContent)
            assert iscreated, "Failed to create %s. Try a different path!" % ff

        # if there is an additional scene include the folder and copy the file if needed.
        if self.scene:
            ff = os.path.join(_basePath, 'scene/extra')
            iscreated = preparedir(ff, removeContent)
            assert iscreated, "Failed to create %s. Try a different path!" % ff

        return _basePath

    # TODO: Write a runmanager class to handle runs
    def run(self, commandFile, debug=False):
        """Run the analysis."""
        assert os.path.isfile(commandFile), \
            ValueError('Failed to find command file: {}'.format(commandFile))

        if debug:
            with open(commandFile, "a") as bf:
                bf.write("\npause\n")

        # FIX: Heroku Permission Patch
        print('Command RUN: {}'.format(commandFile))
        # subprocess.call(commandFile)
        # subprocess.Popen(commandFile, shell=False)
        process = subprocess.Popen(commandFile,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True)

        proc_stdout, errmsg = process.communicate()
        print('Subprocess Log Results:')
        print(proc_stdout)
        print(errmsg)

        self._isCalculated = True
        # self.isChanged = False
        return True

    @property
    def legendParameters(self):
        """Returns suggested legend parameters for this recipe."""
        return None  # for image-based analysis it will be None.

    def write(self):
        """Write contents and commands to a local drive."""
        raise NotImplementedError('write must be implemented in every recipe subclass.')

    def results(self):
        """Return results for this analysis."""
        raise NotImplementedError()

    @staticmethod
    def relpath(path, start):
        """Return a relative path."""
        return os.path.relpath(path, start)
