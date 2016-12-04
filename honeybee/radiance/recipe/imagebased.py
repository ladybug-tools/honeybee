"""Radiance Grid-based Analysis Recipe."""

# from ..postprocess.gridbasedresults import LoadGridBasedDLAnalysisResults
from ._imagebasedbase import GenericImageBasedAnalysisRecipe
from ..parameters.imagebased import ImageBasedParameters
from ..command.oconv import Oconv
from ..command.rpict import Rpict
from ...helper import writeToFile
import os


class ImageBasedAnalysisRecipe(GenericImageBasedAnalysisRecipe):
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
        analysisRecipe = ImageBasedAnalysisRecipe(
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

    # TODO: implemnt isChanged at DaylightAnalysisRecipe level to reload the results
    # if there has been no changes in inputs.
    def __init__(self, sky, views, simulationType=2, radParameters=None,
                 hbObjects=None, subFolder="imagebased"):
        """Create grid-based recipe."""
        GenericImageBasedAnalysisRecipe.__init__(
            self, views, hbObjects, subFolder)

        self.sky = sky
        """A honeybee sky for the analysis."""

        self.simulationType = simulationType
        """Simulation type: 0: Illuminance(lux), 1: Radiation (kWh),
           2: Luminance (Candela) (Default: 0)
        """

        self.radianceParameters = radParameters
        """Radiance parameters for grid based analysis (rtrace).
            (Default: imagebased.LowQualityImage)"""

        # create a result loader to load the results once the analysis is done.
        # self.loader = LoadGridBasedDLAnalysisResults(self.simulationType,
        #                                              self.resultsFile)

    @property
    def simulationType(self):
        """Get/set simulation Type.

        0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela) (Default: 0)
        """
        return self.__simType

    @simulationType.setter
    def simulationType(self, value):
        try:
            value = int(value)
        except:
            value = 0

        assert 0 <= value <= 2, \
            "Simulation type should be between 0-2. Current value: {}".format(value)

        # If this is a radiation analysis make sure the sky is climate-based
        if value == 1:
            assert self.sky.isClimateBased, \
                "The sky for radition analysis should be climate-based."

        self.__simType = value

    @property
    def sky(self):
        """Get and set sky definition."""
        return self.__sky

    @sky.setter
    def sky(self, newSky):
        assert hasattr(newSky, "isRadianceSky"), "%s is not a valid Honeybee sky." % type(newSky)
        self.__sky = newSky

    @property
    def radianceParameters(self):
        """Get and set Radiance parameters."""
        return self.__radianceParameters

    @radianceParameters.setter
    def radianceParameters(self, radParameters):
        if not radParameters:
            radParameters = ImageBasedParameters.LowQuality()
        assert hasattr(radParameters, "isRadianceParameters"), \
            "%s is not a radiance parameters." % type(radParameters)
        self.__radianceParameters = radParameters

    def write(self, targetFolder, projectName='untitled', header=True):
        """Write analysis files to target folder.

        Files for an image based analysis are:
            views <*.vf>: A radiance view.
            sky file <*.sky>: Radiance sky for this analysis.
            material file <*.mat>: Radiance materials. Will be empty if HBObjects is None.
            geometry file <*.rad>: Radiance geometries. Will be empty if HBObjects is None.
            sky file <*.sky>: Radiance sky for this analysis.
            batch file <*.bat>: An executable batch file which has the list of commands.
                oconve <*.sky> <projectName.mat> <projectName.rad> <additional radFiles> > <projectName.oct>
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
        sceneFiles = super(
            ImageBasedAnalysisRecipe, self).populateSubFolders(
                targetFolder, projectName)

        # add view folder
        self.prepareSubFolder(os.path.join(targetFolder, projectName),
                              subFolders=('views',))

        # 1.write views
        viewFiles = self.writeViewsToFile(sceneFiles.path + '\\views')

        # 2.write sky file
        skyFile = self.sky.writeToFile(sceneFiles.path + '\\skies')

        # 3.write batch file
        self.commands = []
        self.resultsFile = []

        if header:
            self.commands.append(self.header(sceneFiles.path))

        # # 4.1.prepare oconv
        octSceneFiles = [skyFile, sceneFiles.matFile, sceneFiles.geoFile] + \
            sceneFiles.matFilesAdd + sceneFiles.radFilesAdd + sceneFiles.octFilesAdd

        oc = Oconv(projectName)
        oc.sceneFiles = tuple(self.relpath(f, sceneFiles.path)
                              for f in octSceneFiles)

        self.commands.append(oc.toRadString())

        # # 4.2.prepare rpict
        # TODO: Add overtrue
        for view, f in zip(self.views, viewFiles):
            rp = Rpict('results\\' + view.name,
                       simulationType=self.simulationType,
                       rpictParameters=self.radianceParameters)
            rp.octreeFile = str(oc.outputFile)
            rp.viewFile = self.relpath(f, sceneFiles.path)

            self.commands.append(rp.toRadString())
            self.resultsFile.append(
                os.path.join(sceneFiles.path, str(rp.outputFile)))

        # # 4.3 write batch file
        batchFile = os.path.join(sceneFiles.path, "commands.bat")

        writeToFile(batchFile, "\n".join(self.commands))

        print "Files are written to: %s" % sceneFiles.path
        return batchFile

    def results(self, flattenResults=True):
        """Return results for this analysis."""
        assert self.isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        # self.loader.simulationType = self.simulationType
        # self.loader.resultFiles = self.resultsFile
        # return self.loader.results
        return self.resultsFile

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
             self.numOfViews)
