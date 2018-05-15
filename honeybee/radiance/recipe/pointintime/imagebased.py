"""Radiance Grid-based Analysis Recipe."""

from .._imagebasedbase import GenericImageBased
from ..recipeutil import write_rad_files, write_extra_files
from ...parameters.rpict import RpictParameters
from ...command.oconv import Oconv
from ...command.rpict import Rpict
from ....futil import write_to_file
import os


class ImageBased(GenericImageBased):
    """Grid base analysis base class.

    Attributes:
        sky: A honeybee sky for the analysis
        views: List of views.
        simulation_type: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 0)
        rad_parameters: Radiance parameters for grid based analysis (rtrace).
            (Default: imagebased.LowQualityImage)
        hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
        sub_folder: Analysis subfolder for this recipe. (Default: "gridbased")

    Usage:
        # create the sky
        sky = SkyWithCertainIlluminanceLevel(2000)

        # initiate analysis_recipe
        analysis_recipe = ImageBased(
            sky, views, simType
            )

        # add honeybee object
        analysis_recipe.hb_objects = HBObjs

        # write analysis files to local drive
        analysis_recipe.write(_folder_, _name_)

        # run the analysis
        analysis_recipe.run(debaug=False)

        # get the results
        print(analysis_recipe.results())
    """

    # TODO: implemnt isChanged at AnalysisRecipe level to reload the results
    # if there has been no changes in inputs.
    def __init__(self, sky, views, simulation_type=2, rad_parameters=None,
                 hb_objects=None, sub_folder="imagebased"):
        """Create grid-based recipe."""
        GenericImageBased.__init__(
            self, views, hb_objects, sub_folder)

        self.sky = sky
        """A honeybee sky for the analysis."""

        self.radiance_parameters = rad_parameters
        """Radiance parameters for grid based analysis (rtrace).
            (Default: imagebased.LowQualityImage)"""

        self.simulation_type = simulation_type
        """Simulation type: 0: Illuminance(lux), 1: Radiation (kWh),
           2: Luminance (Candela) (Default: 0)
        """

    @property
    def simulation_type(self):
        """Get/set simulation Type.

        0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela) (Default: 0)
        """
        return self._simType

    @simulation_type.setter
    def simulation_type(self, value):
        try:
            value = int(value)
        except TypeError:
            value = 0

        assert 0 <= value <= 2, \
            "Simulation type should be between 0-2. Current value: {}".format(value)

        # If this is a radiation analysis make sure the sky is climate-based
        if value == 1:
            assert self.sky.is_climate_based, \
                "The sky for radition analysis should be climate-based."

        self._simType = value
        self.sky.sky_type = value
        if self._simType < 2:
            self.radiance_parameters.irradiance_calc = True
        else:
            self.radiance_parameters.irradiance_calc = None

    @property
    def sky(self):
        """Get and set sky definition."""
        return self._sky

    @sky.setter
    def sky(self, new_sky):
        assert hasattr(new_sky, 'isRadianceSky'), \
            TypeError('%s is not a valid Honeybee sky.' % type(new_sky))
        assert new_sky.is_point_in_time, \
            TypeError('Sky must be one of the point-in-time skies.')

        self._sky = new_sky.duplicate()

    @property
    def radiance_parameters(self):
        """Get and set Radiance parameters."""
        return self._radiance_parameters

    @radiance_parameters.setter
    def radiance_parameters(self, rad_parameters):
        if not rad_parameters:
            rad_parameters = RpictParameters.low_quality()
        assert hasattr(rad_parameters, "isRadianceParameters"), \
            "%s is not a radiance parameters." % type(rad_parameters)
        self._radiance_parameters = rad_parameters

    def write(self, target_folder, project_name='untitled', header=True):
        """Write analysis files to target folder.

        Files for an image based analysis are:
            views <*.vf>: A radiance view.
            sky file <*.sky>: Radiance sky for this analysis.
            material file <*.mat>: Radiance materials. Will be empty if hb_objects is
                None.
            geometry file <*.rad>: Radiance geometries. Will be empty if hb_objects is
                None.
            sky file <*.sky>: Radiance sky for this analysis.
            batch file <*.bat>: An executable batch file which has the list of commands.
                oconve <*.sky> <project_name.mat> <project_name.rad>
                <additional rad_files> > <project_name.oct>
                rtrace <radiance_parameters> <project_name.oct> > <project_name.res>
            results file <*.hdr>: Results file once the analysis is over.

        Args:
            target_folder: Path to parent folder. Files will be created under
                target_folder/gridbased. use self.sub_folder to change subfolder name.
            project_name: Name of this project as a string.

        Returns:
            Full path to command.bat
        """
        # 0.prepare target folder
        # create main folder target_folder/project_name
        project_folder = \
            super(ImageBased, self).write_content(
                target_folder, project_name, subfolders=['view'])

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = write_rad_files(
            project_folder + '/scene', project_name, self.opaque_rad_file,
            self.glazing_rad_file, self.window_groups_rad_files
        )
        # additional radiance files added to the recipe as scene
        extrafiles = write_extra_files(self.scene, project_folder + '/scene')

        # 1.write views
        view_files = self.write_views(project_folder + '/view')

        # 2.write batch file
        if header:
            self.commands.append(self.header(project_folder))

        # 3.write sky file
        self._commands.append(self.sky.to_rad_string(folder='sky'))

        # 3.1. write ground and sky materials
        skyground = self.sky.write_sky_ground(os.path.join(project_folder, 'sky'))

        # TODO(Mostapha): add window_groups here if any!
        # # 4.1.prepare oconv
        oct_scene_files = \
            [os.path.join(project_folder, str(self.sky.command('sky').output_file)),
             skyground] + opqfiles + glzfiles + wgsfiles + extrafiles.fp

        oc = Oconv(project_name)
        oc.scene_files = tuple(self.relpath(f, project_folder)
                               for f in oct_scene_files)

        self._commands.append(oc.to_rad_string())

        # # 4.2.prepare rpict
        # TODO: Add overtrue
        for view, f in zip(self.views, view_files):
            # set x and y resolution based on x and y resolution in view
            self.radiance_parameters.x_resolution = view.x_resolution
            self.radiance_parameters.y_resolution = view.y_resolution

            rp = Rpict('result/' + view.name,
                       simulation_type=self.simulation_type,
                       rpict_parameters=self.radiance_parameters)
            rp.octree_file = str(oc.output_file)
            rp.view_file = self.relpath(f, project_folder)

            self._commands.append(rp.to_rad_string())
            self._result_files.append(
                os.path.join(project_folder, str(rp.output_file)))

        # # 4.3 write batch file
        batch_file = os.path.join(project_folder, "commands.bat")

        write_to_file(batch_file, "\n".join(self.commands))

        return batch_file

    def results(self):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        return self._result_files

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represent grid based recipe."""
        _analysisType = {
            0: "Illuminance", 1: "Radiation", 2: "Luminance"
        }
        return "%s: %s\n#Views: %d" % \
            (self.__class__.__name__,
             _analysisType[self.simulation_type],
             self.view_count)
