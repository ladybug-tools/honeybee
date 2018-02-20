"""Base class for RADIANCE Analysis Recipes."""
from ...futil import preparedir, get_radiance_path_lines
from .recipeutil import input_srfs_to_rad_files

import os
import subprocess


class AnalysisRecipe(object):
    """Analysis Recipe Base class.

    Attributes:
        hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
        sub_folder: Sub-folder for this analysis recipe. (e.g. "gridbased")
    """

    def __init__(self, hb_objects=None, sub_folder=None, scene=None):
        """Create Analysis recipe."""
        self.hb_objects = hb_objects
        """An optional list of Honeybee surfaces or zones. (Default: None)"""

        self.sub_folder = sub_folder
        """Sub-folder for this analysis recipe. (e.g. "gridbased", "imagebased")"""

        self.scene = scene
        """Additional Radiance files other than honeybee objects."""

        self._rad_file = None
        self._hbObjs = ()
        self._radiance_materials = ()
        self._commands = []
        self._result_files = []
        self._isCalculated = False
        self.isChanged = True

    @classmethod
    def from_json(cls):
        """Create analysis grid from json object."""
        raise NotImplementedError(
            "from_json is not implemented for {}.".format(cls.__class__.__name__)
        )

    @property
    def isAnalysisRecipe(self):
        """Return true to indicate it is an analysis recipe."""
        return True

    @property
    def is_calculated(self):
        """Return True if the recipe is calculated."""
        return self._isCalculated

    @property
    def result_files(self):
        """Get list of result files for this recipe."""
        return self._result_files

    @property
    def commands(self):
        """List of recipe commands."""
        return self._commands

    @property
    def hb_objects(self):
        """Get and set Honeybee objects for this recipe."""
        return self._hbObjs

    @hb_objects.setter
    def hb_objects(self, hb_objects):
        if not hb_objects:
            self._hbObjs = ()
            self._opaque = None
            self._glazing = None
            self._wgs = ()
        else:
            self._hbObjs = []
            try:
                for obj in hb_objects:
                    if hasattr(obj, 'isHBZone'):
                        self._hbObjs.extend(obj.surfaces)
                        for srf in obj.surfaces:
                            self._hbObjs.extend(srf.children_surfaces)
                    elif obj.isHBAnalysisSurface:
                        self._hbObjs.append(obj)
                        try:
                            self._hbObjs.extend(obj.children_surfaces)
                        except AttributeError:
                            # HBFenSurfaces
                            pass
            except AttributeError as e:
                raise TypeError(
                    'Object inputs must be Honeybee Zones or Surfaces:\n{}'.format(e)
                )

        self._opaque, self._glazing, self._wgs = input_srfs_to_rad_files(self._hbObjs)

    @property
    def opaque_surfaces(self):
        """Collection of opaque surfaces in this recipe."""
        return self._opaque.hb_surfaces

    @property
    def glazing_surfaces(self):
        """Collection of glazing surfaces in this recipe."""
        return self._glazing.hb_surfaces

    @property
    def window_groups(self):
        """Collection of window groups in this recipe."""
        return tuple(wg.hb_surfaces[0] for wg in self._wgs)

    @property
    def opaque_rad_file(self):
        """A RadFile for opaque surfaces in this recipe."""
        return self._opaque

    @property
    def glazing_rad_file(self):
        """A RadFile for glazing surfaces in this recipe."""
        return self._glazing

    @property
    def window_groups_rad_files(self):
        """Collection of RadFiles for window groups in this recipe."""
        return self._wgs

    @property
    def sub_folder(self):
        """Sub-folder for Grid-based analysis."""
        return self._sub_folder

    @sub_folder.setter
    def sub_folder(self, value):
        """Sub-folder for Grid-based analysis."""
        self._sub_folder = str(value)

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

    def header(self, target_folder, includ_rad_path=True):
        """Get the header for bat file.

        The header changes the path into project path and also add lines to set PATH and
        PATHRAY for Radiance.

        IncludeRadPath is only useful for Windows.

        Args:
            target_folder: Full path to working directory.
            includ_rad_path: At the Boolean to True to include path to radiance
                installation folder.
        """
        dir_line = "%s\ncd %s\n" % (os.path.splitdrive(target_folder)[0], target_folder)

        if includ_rad_path:
            return '\n'.join((get_radiance_path_lines(), dir_line))
        else:
            return dir_line

    # TODO: Get commands without running write method.
    def to_rad_string(self):
        """Radiance representation of the recipe."""
        assert len(self.commands) != 0, \
            Exception('You must write the recipe to get the list of commands'
                      ' as rad_string.')
        return '\n'.join(self.commands)

    def write_content(self, target_folder, project_name='untitled', remove_content=True,
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
        self._result_files = []

        if not target_folder:
            target_folder = os.path.join(os.environ['USERPROFILE'], 'honeybee')

        iscreated = preparedir(target_folder, False)
        assert iscreated, "Failed to create %s. Try a different path!" % target_folder

        project_name = project_name or 'untitled'

        _basePath = os.path.join(target_folder, project_name, self.sub_folder)
        iscreated = preparedir(_basePath, remove_content=False)
        assert iscreated, "Failed to create %s. Try a different path!" % _basePath

        print('Writing recipe contents to: %s' % _basePath)

        # create subfolders inside the folder
        subfolders += ['scene', 'sky', 'result']
        for folder in subfolders:
            ff = os.path.join(_basePath, folder)
            iscreated = preparedir(ff, remove_content)
            assert iscreated, "Failed to create %s. Try a different path!" % ff

        # if there is an additional scene include the folder and copy the file if needed.
        if self.scene:
            ff = os.path.join(_basePath, 'scene/extra')
            iscreated = preparedir(ff, remove_content)
            assert iscreated, "Failed to create %s. Try a different path!" % ff

        return _basePath

    # TODO: Write a runmanager class to handle runs
    def run(self, command_file, debug=False):
        """Run the analysis."""
        assert os.path.isfile(command_file), \
            ValueError('Failed to find command file: {}'.format(command_file))

        if debug:
            with open(command_file, "a") as bf:
                bf.write("\npause\n")

        # FIX: Heroku Permission Patch
        subprocess.call(command_file)
        # print('Command RUN: {}'.format(command_file))
        # process = subprocess.Popen(command_file,
        #                            stdout=subprocess.PIPE,
        #                            stderr=subprocess.PIPE,
        #                            shell=True)
        #
        # proc_stdout, errmsg = process.communicate()
        # print('Subprocess Log Results:')
        # print(proc_stdout)
        # print('ERRORS:\n{}'.format(errmsg))

        self._isCalculated = True
        # self.isChanged = False
        return True

    @property
    def legend_parameters(self):
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
        try:
            return os.path.relpath(path, start)
        except AttributeError:
            raise TypeError('Failed to convert to relative path: {}'.format(path))
