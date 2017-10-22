"""Radiance Grid-based Analysis Recipe."""
from .._gridbasedbase import GenericGridBased
from ..recipeutil import writeRadFiles, writeExtraFiles
from ...parameters.gridbased import LowQuality
from ...command.oconv import Oconv
from ...command.rtrace import Rtrace
from ...command.rcalc import Rcalc
from ....futil import writeToFile
from ...analysisgrid import AnalysisGrid
from ....hbsurface import HBSurface
from ...sky.cie import CIE

from ladybug.dt import DateTime

import os


class GridBased(GenericGridBased):
    """Grid base analysis base class.

    Attributes:
        sky: A honeybee sky for the analysis
        analysisGrids: List of analysis grids.
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
        analysisRecipe = GridBased(
            sky, testPoints, ptsVectors, simType
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
    def __init__(self, sky, analysisGrids, simulationType=0, radParameters=None,
                 hbObjects=None, subFolder="gridbased"):
        """Create grid-based recipe."""
        GenericGridBased.__init__(
            self, analysisGrids, hbObjects, subFolder)

        self.sky = sky
        """A honeybee sky for the analysis."""

        self.radianceParameters = radParameters
        """Radiance parameters for grid based analysis (rtrace).
            (Default: gridbased.LowQuality)"""

        self.simulationType = simulationType
        """Simulation type: 0: Illuminance(lux), 1: Radiation (wh),
           2: Luminance (Candela) (Default: 0)
        """

    @classmethod
    def fromJson(cls, recJson):
        """Create the solar access recipe from json.
        {
          "id": 1, // do NOT overwrite this id
          "sky": null, // a honeybee sky
          "surfaces": [], // list of honeybee surfaces
          "analysis_grids": [] // list of analysis grids
          "analysis_type": 0 // [0] illuminance(lux), [1] radiation (kwh), [2] luminance (Candela).
        }
        """
        sky = CIE.fromJson(recJson['sky'])
        analysisGrids = \
            tuple(AnalysisGrid.fromJson(ag) for ag in recJson['analysis_grids'])
        hbObjects = tuple(HBSurface.fromJson(srf) for srf in recJson['surfaces'])
        return cls(sky, analysisGrids, recJson['analysis_type'], None, hbObjects)

    @classmethod
    def fromPointsAndVectors(cls, sky, pointGroups, vectorGroups=None,
                             simulationType=0, radParameters=None,
                             hbObjects=None, subFolder="gridbased"):
        """Create grid based recipe from points and vectors.

        Args:
            sky: A honeybee sky for the analysis
            pointGroups: A list of (x, y, z) test points or lists of (x, y, z)
                test points. Each list of test points will be converted to a
                TestPointGroup. If testPts is a single flattened list only one
                TestPointGroup will be created.
            vectorGroups: An optional list of (x, y, z) vectors. Each vector
                represents direction of corresponding point in testPts. If the
                vector is not provided (0, 0, 1) will be assigned.
            simulationType: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance
                (Candela) (Default: 0).
            radParameters: Radiance parameters for grid based analysis (rtrace).
                (Default: gridbased.LowQuality)
            hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
            subFolder: Analysis subfolder for this recipe. (Default: "gridbased")
        """
        analysisGrids = cls.analysisGridsFromPointsAndVectors(pointGroups,
                                                              vectorGroups)
        return cls(sky, analysisGrids, simulationType, radParameters, hbObjects,
                   subFolder)

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
        if self.sky.isClimateBased:
            self.sky.skyType = value

    @property
    def sky(self):
        """Get and set sky definition."""
        return self._sky

    @sky.setter
    def sky(self, newSky):
        assert hasattr(newSky, 'isRadianceSky'), \
            '%s is not a valid Honeybee sky.' % type(newSky)
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
            radParameters = LowQuality()
        assert hasattr(radParameters, "isRadianceParameters"), \
            "%s is not a radiance parameters." % type(radParameters)
        self._radianceParameters = radParameters

    def write(self, targetFolder, projectName='untitled', header=True):
        """Write analysis files to target folder.

        Files for a grid based analysis are:
            test points <projectName.pts>: List of analysis points.
            sky file <*.sky>: Radiance sky for this analysis.
            material file <*.mat>: Radiance materials. Will be empty if HBObjects
                is None.
            geometry file <*.rad>: Radiance geometries. Will be empty if HBObjects
                is None.
            sky file <*.sky>: Radiance sky for this analysis.
            batch file <*.bat>: An executable batch file which has the list of commands.
                oconve <*.sky> <projectName.mat> <projectName.rad> <additional radFiles>
                    > <projectName.oct>
                rtrace <radianceParameters> <projectName.oct> > <projectName.res>
            results file <*.res>: Results file once the analysis is over.

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
            super(GenericGridBased, self).writeContent(targetFolder, projectName)

        # write geometry and material files
        opqfiles, glzfiles, wgsfiles = writeRadFiles(
            projectFolder + '/scene', projectName, self.opaqueRadFile,
            self.glazingRadFile, self.windowGroupsRadFiles
        )
        # additional radiance files added to the recipe as scene
        extrafiles = writeExtraFiles(self.scene, projectFolder + '/scene')

        # 1.write points
        pointsFile = self.writeAnalysisGrids(projectFolder, projectName)

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
        oc.sceneFiles = tuple(self.relpath(f, projectFolder) for f in octSceneFiles)

        # # 4.2.prepare rtrace
        rt = Rtrace('result/' + projectName,
                    simulationType=self.simulationType,
                    radianceParameters=self.radianceParameters)
        rt.radianceParameters.h = True
        rt.octreeFile = str(oc.outputFile)
        rt.pointsFile = self.relpath(pointsFile, projectFolder)

        # # 4.3. add rcalc to convert rgb values to irradiance
        rc = Rcalc('result/{}.ill'.format(projectName), str(rt.outputFile))

        if os.name == 'nt':
            rc.rcalcParameters.expression = '"$1=(0.265*$1+0.67*$2+0.065*$3)*179"'
        else:
            rc.rcalcParameters.expression = "'$1=(0.265*$1+0.67*$2+0.065*$3)*179'"

        # # 4.4 write batch file
        self._commands.append(oc.toRadString())
        self._commands.append(rt.toRadString())
        self._commands.append(rc.toRadString())

        batchFile = os.path.join(projectFolder, "commands.bat")

        writeToFile(batchFile, "\n".join(self.commands))

        self._resultFiles = os.path.join(projectFolder, str(rc.outputFile))

        return batchFile

    def results(self):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        print('Unloading the current values from the analysis grids.')
        for ag in self.analysisGrids:
            ag.unload()

        sky = self.sky
        dt = DateTime(sky.month, sky.day, int(sky.hour),
                      int(60 * (sky.hour - int(sky.hour))))

        rf = self._resultFiles
        startLine = 0
        mode = 179 if self.simulationType == 1 else 0

        for count, analysisGrid in enumerate(self.analysisGrids):
            if count:
                startLine += len(self.analysisGrids[count - 1])

            analysisGrid.setValuesFromFile(
                rf, (int(dt.hoy),), startLine=startLine, header=False, mode=mode
            )

        return self.analysisGrids

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represent grid based recipe."""
        _analysisType = {
            0: "Illuminance", 1: "Radiation", 2: "Luminance"
        }
        return "%s: %s\n#PointGroups: %d #Points: %d" % \
            (self.__class__.__name__,
             _analysisType[self.simulationType],
             self.AnalysisGridCount,
             self.totalPointCount)

    def toJson(self):
        """Create point-in-time recipe from json.
            {
              "id": 1, // do NOT overwrite this id
              "sky": null, // a honeybee sky
              "surfaces": [], // list of honeybee surfaces
              "analysis_grids": [] // list of analysis grids
              "analysis_type": 0 // [0] illuminance(lux), [1] radiation (kwh), [2] luminance (Candela).
            }
        """
        return {
            "id": 1,
            "sky": self.sky.toJson(),
            "surfaces": [srf.toJson() for srf in self.hbObjects],
            "analysis_grids": [ag.toJson() for ag in self.analysisGrids],
            "analysis_type": self.simulationType
        }
