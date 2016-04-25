"""Radiance Grid-based Analysis Recipe."""

from ..postprocess.gridbasedresults import LoadGridBasedDLAnalysisResults
from ._gridbasedbase import HBGenericGridBasedAnalysisRecipe
from ..parameters.gridbased import LowQuality
from ..command.oconv import Oconv
from ..command.rtrace import Rtrace
from ...helper import preparedir

import os
import subprocess


class HBGridBasedAnalysisRecipe(HBGenericGridBasedAnalysisRecipe):
    """Grid base analysis base class.

    Attributes:
        sky: A honeybee sky for the analysis
        pointGroups: A list of (x, y, z) test points or lists of (x, y, z) test points.
            Each list of test points will be converted to a TestPointGroup. If testPts
            is a single flattened list only one TestPointGroup will be created.
        vectorGroups: An optional list of (x, y, z) vectors. Each vector represents direction
            of corresponding point in testPts. If the vector is not provided (0, 0, 1)
            will be assigned.
        simulationType: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 0)
        radParameters: Radiance parameters for grid based analysis (rtrace).
            (Default: gridbased.LowQuality)
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "gridbased")

    Usage:
        # create the sky
        sky = SkyWithCertainIlluminanceLevel(2000)

        # initiate analysisRecipe
        analysisRecipe = HBGridBasedAnalysisRecipe(
            sky, testPoints, ptsVectors, simType
            )

        # add honeybee object
        analysisRecipe.hbObjects = HBObjs

        # write analysis files to local drive
        analysisRecipe.writeToFile(_folder_, _name_)

        # run the analysis
        analysisRecipe.run(debaug=False)

        # get the results
        print analysisRecipe.results()
    """

    # TODO: implemnt isChanged at HBDaylightAnalysisRecipe level to reload the results
    # if there has been no changes in inputs.
    def __init__(self, sky, pointGroups, vectorGroups=[], simulationType=0,
                 radParameters=None, hbObjects=None, subFolder="gridbased"):
        """Create grid-based recipe."""
        HBGenericGridBasedAnalysisRecipe.__init__(self, pointGroups=pointGroups,
                                                  vectorGroups=vectorGroups,
                                                  hbObjects=hbObjects,
                                                  subFolder=subFolder)

        self.sky = sky
        """A honeybee sky for the analysis."""

        self.simulationType = simulationType
        """Simulation type: 0: Illuminance(lux), 1: Radiation (kWh),
           2: Luminance (Candela) (Default: 0)
        """

        self.radianceParameters = radParameters
        """Radiance parameters for grid based analysis (rtrace).
            (Default: gridbased.LowQuality)"""

        self.__batchFile = None
        self.resultsFile = []
        # create a result loader to load the results once the analysis is done.
        self.loader = LoadGridBasedDLAnalysisResults(self.simulationType,
                                                     self.resultsFile)

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
            radParameters = LowQuality()
        assert hasattr(radParameters, "isRadianceParameters"), \
            "%s is not a radiance parameters." % type(radParameters)
        self.__radianceParameters = radParameters

    # TODO: Add path to PATH and use relative path in batch files
    def writeToFile(self, targetFolder, projectName, radFiles=None,
                    useRelativePath=False):
        """Write analysis files to target folder.

        Files for a grid based analysis are:
            test points <projectName.pts>: List of analysis points.
            sky file <*.sky>: Radiance sky for this analysis.
            material file <*.mat>: Radiance materials. Will be empty if HBObjects is None.
            geometry file <*.rad>: Radiance geometries. Will be empty if HBObjects is None.
            sky file <*.sky>: Radiance sky for this analysis.
            batch file <*.bat>: An executable batch file which has the list of commands.
                oconve <*.sky> <projectName.mat> <projectName.rad> <additional radFiles> > <projectName.oct>
                rtrace <radianceParameters> <projectName.oct> > <projectName.res>
            results file <*.res>: Results file once the analysis is over.

        Args:
            targetFolder: Path to parent folder. Files will be created under
                targetFolder/gridbased. use self.subFolder to change subfolder name.
            projectName: Name of this project as a string.
            radFiles: A list of additional .rad files to be added to the scene
            useRelativePath: Set to True to use relative path in bat file <NotImplemented!>.

        Returns:
            True in case of success.
        """
        # 0.prepare target folder
        # create main folder targetFolder\projectName
        _basePath = os.path.join(targetFolder, projectName)
        _ispath = preparedir(_basePath)
        assert _ispath, "Failed to create %s. Try a different path!" % _basePath

        # create main folder targetFolder\projectName\gridbased
        _path = os.path.join(_basePath, self.subFolder)
        _ispath = preparedir(_path)

        assert _ispath, "Failed to create %s. Try a different path!" % _path

        # Check if anything has changed
        # if not self.isChanged:
        #     print "Inputs has not changed! Check files at %s" % _path

        # 1.write sky file
        skyFile = self.sky.writeToFile(_path)

        # 2.write points
        pointsFile = self.writePointsToFile(_path, projectName)

        # 3.write materials and geometry files
        matFile, geoFile = self.writeHBObjectsToFile(_path, projectName)

        # 4.write batch file
        batchFileLines = []

        # TODO: This line won't work in linux.
        dirLine = "%s\ncd %s" % (os.path.splitdrive(_path)[0], _path)
        batchFileLines.append(dirLine)

        # # 4.1.prepare oconv
        oc = Oconv(projectName)
        oc.sceneFiles = [skyFile, matFile, geoFile]

        # # 4.2.prepare rtrace
        rt = Rtrace(projectName,
                    simulationType=self.simulationType,
                    radianceParameters=self.radianceParameters)
        rt.radianceParameters.h = True
        rt.octreeFile = os.path.join(_path, projectName + ".oct")
        rt.pointFile = pointsFile

        # # 4.3 write batch file
        batchFileLines.append(oc.toRadString())
        batchFileLines.append(rt.toRadString())
        batchFile = os.path.join(_path, projectName + ".bat")

        self.write(batchFile, "\n".join(batchFileLines))

        self.__batchFile = batchFile

        print "Files are written to: %s" % _path
        return _path

    # TODO: Update the method to batch run and move it to baseclass
    def run(self, debug=False):
        """Run the analysis."""
        if self.__batchFile:
            if debug:
                with open(self.__batchFile, "a") as bf:
                    bf.write("\npause")

            subprocess.call(self.__batchFile)

            self.isCalculated = True
            # self.isChanged = False

            self.resultsFile = [self.__batchFile.replace(".bat", ".res")]
            return True
        else:
            raise Exception("You need to write the files before running the recipe.")

    def results(self, flattenResults=True):
        """Return results for this analysis."""
        assert self.isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        self.loader.simulationType = self.simulationType
        self.loader.resultFiles = self.resultsFile
        return self.loader.results

    def __repr__(self):
        """Represent grid based recipe."""
        _analysisType = {
            0: "Illuminance", 1: "Radiation", 2: "Luminance"
        }
        return "%s: %s\n#PointGroups: %d #Points: %d" % \
            (self.__class__.__name__,
             _analysisType[self.simulationType],
             self.numOfPointGroups,
             self.numOfTotalPoints)
