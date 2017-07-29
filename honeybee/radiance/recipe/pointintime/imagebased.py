"""Radiance Grid-based Analysis Recipe."""

from .._imagebasedbase import GenericImageBased
from ..recipeutil import writeRadFiles, writeExtraFiles
from ...parameters.imagebased import ImageBasedParameters
from ...command.oconv import Oconv
from ...command.rpict import Rpict
from ....futil import writeToFile
import os


class ImageBased(GenericImageBased):
    """Grid base analysis base class.

    Attributes:
        sky: A honeybee sky for the analysis
        views: List of views.
        simulationType: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 0)
        radParameters: Radiance parameters for grid based analysis (rtrace).
            (Default: imagebased.LowQualityImage)
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "gridbased")

    Usage:
        # create the sky
        sky = SkyWithCertainIlluminanceLevel(2000)

        # initiate analysisRecipe
        analysisRecipe = ImageBased(
            sky, views, simType
            )

        # add honeybee object
        analysisRecipe.hbObjects = HBObjs

        # write analysis files to local drive
        analysisRecipe.write(_folder_, _name_)

        # run the analysis
        analysisRecipe.run(debaug=False)

        # get the results
        print analysisRecipe.results()
    """

    # TODO: implemnt isChanged at AnalysisRecipe level to reload the results
    # if there has been no changes in inputs.
    def __init__(self, sky, views, simulationType=2, radParameters=None,
                 hbObjects=None, subFolder="imagebased"):
        """Create grid-based recipe."""
        GenericImageBased.__init__(
            self, views, hbObjects, subFolder)

        self.sky = sky
        """A honeybee sky for the analysis."""

        self.radianceParameters = radParameters
        """Radiance parameters for grid based analysis (rtrace).
            (Default: imagebased.LowQualityImage)"""

        self.simulationType = simulationType
        """Simulation type: 0: Illuminance(lux), 1: Radiation (kWh),
           2: Luminance (Candela) (Default: 0)
        """

    @property
    def simulationType(self):
        """Get/set simulation Type.

        0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela) (Default: 0)
        """
        return self._simType

    @simulationType.setter
    def simulationType(self, value):
        try:
            value = int(value)
        except TypeError:
            value = 0

        assert 0 <= value <= 2, \
            "Simulation type should be between 0-2. Current value: {}".format(value)

        # If this is a radiation analysis make sure the sky is climate-based
        if value == 1:
            assert self.sky.isClimateBased, \
                "The sky for radition analysis should be climate-based."

        self._simType = value
        self.sky.skyType = value
        if self._simType < 2:
            self.radianceParameters.irradianceCalc = True
        else:
            self.radianceParameters.irradianceCalc = None

    @property
    def sky(self):
        """Get and set sky definition."""
        return self._sky

    @sky.setter
    def sky(self, newSky):
        assert hasattr(newSky, 'isRadianceSky'), \
            TypeError('%s is not a valid Honeybee sky.' % type(newSky))
        assert newSky.isPointInTime, \
            TypeError('Sky must be one of the point-in-time skies.')

        self._sky = newSky.duplicate()

    @property
    def radianceParameters(self):
        """Get and set Radiance parameters."""
        return self._radianceParameters

    @radianceParameters.setter
    def radianceParameters(self, radParameters):
        if not radParameters:
            radParameters = ImageBasedParameters.LowQuality()
        assert hasattr(radParameters, "isRadianceParameters"), \
            "%s is not a radiance parameters." % type(radParameters)
        self._radianceParameters = radParameters

    def write(self, targetFolder, projectName='untitled', header=True):
        """Write analysis files to target folder.

        Files for an image based analysis are:
            views <*.vf>: A radiance view.
            sky file <*.sky>: Radiance sky for this analysis.
            material file <*.mat>: Radiance materials. Will be empty if HBObjects is
                None.
            geometry file <*.rad>: Radiance geometries. Will be empty if HBObjects is
                None.
            sky file <*.sky>: Radiance sky for this analysis.
            batch file <*.bat>: An executable batch file which has the list of commands.
                oconve <*.sky> <projectName.mat> <projectName.rad> <additional radFiles>
                > <projectName.oct>
                rtrace <radianceParameters> <projectName.oct> > <projectName.res>
            results file <*.hdr>: Results file once the analysis is over.

        Args:
            targetFolder: Path to parent folder. Files will be created under
                targetFolder/gridbased. use self.subFolder to change subfolder name.
            projectName: Name of this project as a string.

        Returns:
            Full path to command.bat
        """
        # 0.prepare target folder
        # create main folder targetFolder\projectName
        projectFolder = \
            super(ImageBased, self).writeContent(
                targetFolder, projectName, subfolders=['view'])

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = writeRadFiles(
            projectFolder + '/scene', projectName, self.opaqueRadFile,
            self.glazingRadFile, self.windowGroupsRadFiles
        )
        # additional radiance files added to the recipe as scene
        extrafiles = writeExtraFiles(self.scene, projectFolder + '/scene')

        # 1.write views
        viewFiles = self.writeViews(projectFolder + '\\view')

        # 2.write batch file
        if header:
            self.commands.append(self.header(projectFolder))

        # 3.write sky file
        self._commands.append(self.sky.toRadString(folder='sky'))

        # 3.1. write ground and sky materials
        skyground = self.sky.writeSkyGround(os.path.join(projectFolder, 'sky'))

        # TODO(Mostapha): add windowGroups here if any!
        # # 4.1.prepare oconv
        octSceneFiles = \
            [os.path.join(projectFolder, str(self.sky.command('sky').outputFile)),
             skyground] + opqfiles + glzfiles + wgsfiles + extrafiles.fp

        oc = Oconv(projectName)
        oc.sceneFiles = tuple(self.relpath(f, projectFolder)
                              for f in octSceneFiles)

        self._commands.append(oc.toRadString())

        # # 4.2.prepare rpict
        # TODO: Add overtrue
        for view, f in zip(self.views, viewFiles):
            rp = Rpict('result\\' + view.name,
                       simulationType=self.simulationType,
                       rpictParameters=self.radianceParameters)
            rp.octreeFile = str(oc.outputFile)
            rp.viewFile = self.relpath(f, projectFolder)

            self._commands.append(rp.toRadString())
            self._resultFiles.append(
                os.path.join(projectFolder, str(rp.outputFile)))

        # # 4.3 write batch file
        batchFile = os.path.join(projectFolder, "commands.bat")

        writeToFile(batchFile, "\n".join(self.commands))

        return batchFile

    def results(self):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        return self._resultFiles

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
             _analysisType[self.simulationType],
             self.viewCount)
