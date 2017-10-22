"""Radiance Solar Access Grid-based Analysis Recipe."""
from .._gridbasedbase import GenericGridBased
from ..recipeutil import writeRadFiles, writeExtraFiles
from ..recipedcutil import RGBMatrixFileToIll
from ...parameters.rcontrib import RcontribParameters
from ...command.oconv import Oconv
from ...command.rcontrib import Rcontrib
from ...analysisgrid import AnalysisGrid
from ....futil import writeToFile
from ....vectormath.euclid import Vector3
from ....hbsurface import HBSurface

from ladybug.sunpath import Sunpath
from ladybug.location import Location
from ladybug.legendparameters import LegendParameters
from ladybug.color import Colorset

import os


class SolarAccessGridBased(GenericGridBased):
    """Solar access recipe.

    This class calculates number of sunlight hours for a group of test points.

    Attributes:
        sunVectors: A list of ladybug sun vectors as (x, y, z) values. Z value
            for sun vectors should be negative (coming from sun toward earth)
        hoys: A list of hours of the year for each sun vector.
        analysisGrids: List of analysis grids.
        timestep: The number of timesteps per hour for sun vectors. This number
            should be smaller than 60 and divisible by 60. The default is set to
            1 such that one sun vector is generated for each hour (Default: 1).
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "sunlighthours")

    Usage:
        # initiate analysisRecipe
        analysisRecipe = SolarAccess(sunVectors, analysisGrids)

        # add honeybee object
        analysisRecipe.hbObjects = HBObjs

        # write analysis files to local drive
        analysisRecipe.writeToFile(_folder_, _name_)

        # run the analysis
        analysisRecipe.run(debaug=False)

        # get the results
        print analysisRecipe.results()
    """

    def __init__(self, sunVectors, hoys, analysisGrids, timestep=1, hbObjects=None,
                 subFolder='solaraccess'):
        """Create sunlighthours recipe."""
        GenericGridBased.__init__(
            self, analysisGrids, hbObjects, subFolder
        )

        assert len(hoys) == len(sunVectors), \
            ValueError(
                'Length of sunVectors [] must be equall to '
                'the length of hoys []'.format(len(sunVectors), len(hoys))
        )
        self.sunVectors = sunVectors
        self._hoys = hoys
        self.timestep = timestep

        self._radianceParameters = RcontribParameters()
        self._radianceParameters.irradianceCalc = True
        self._radianceParameters.ambientBounces = 0
        self._radianceParameters.directCertainty = 1
        self._radianceParameters.directThreshold = 0
        self._radianceParameters.directJitter = 0

    @classmethod
    def fromJson(cls, recJson):
        """Create the solar access recipe from json.
            {
              "id": 0, // do NOT overwrite this id
              "location": null, // a honeybee location - see below
              "hoys": [], // list of hours of the year
              "surfaces": [], // list of honeybee surfaces
              "analysis_grids": [] // list of analysis grids
              "sun_vectors": [] // list of sun vectors if location is not provided
            }
        """
        hoys = recJson["hoys"]
        if 'sun_vectors' not in recJson or not recJson['sun_vectors']:
            loc = Location.fromJson(recJson['location'])
            sp = Sunpath.fromLocation(loc)
            suns = (sp.calculateSunFromHOY(HOY) for HOY in hoys)
            sunVectors = tuple(s.sunVector for s in suns if s.isDuringDay)
        else:
            sunVectors = recJson['sun_vectors']

        analysisGrids = \
            tuple(AnalysisGrid.fromJson(ag) for ag in recJson["analysis_grids"])
        hbObjects = tuple(HBSurface.fromJson(srf) for srf in recJson["surfaces"])
        return cls(sunVectors, hoys, analysisGrids, 1, hbObjects)

    @classmethod
    def fromPointsAndVectors(cls, sunVectors, hoys, pointGroups, vectorGroups=[],
                             timestep=1, hbObjects=None, subFolder='sunlighthour'):
        """Create sunlighthours recipe from points and vectors.

        Args:
            sunVectors: A list of ladybug sun vectors as (x, y, z) values. Z value
                for sun vectors should be negative (coming from sun toward earth)
            hoys: A list of hours of the year for each sun vector.
            pointGroups: A list of (x, y, z) test points or lists of (x, y, z) test
                points. Each list of test points will be converted to a
                TestPointGroup. If testPts is a single flattened list only one
                TestPointGroup will be created.
            vectorGroups: An optional list of (x, y, z) vectors. Each vector
                represents direction of corresponding point in testPts. If the
                vector is not provided (0, 0, 1) will be assigned.
            timestep: The number of timesteps per hour for sun vectors. This number
                should be smaller than 60 and divisible by 60. The default is set to
                1 such that one sun vector is generated for each hour (Default: 1).
            hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
            subFolder: Analysis subfolder for this recipe. (Default: "sunlighthours")
        """
        analysisGrids = cls.analysisGridsFromPointsAndVectors(pointGroups,
                                                              vectorGroups)
        return cls(sunVectors, hoys, analysisGrids, timestep, hbObjects, subFolder)

    @classmethod
    def fromSuns(cls, suns, pointGroups, vectorGroups=[], timestep=1,
                 hbObjects=None, subFolder='sunlighthour'):
        """Create sunlighthours recipe from LB sun objects.

        Attributes:
            suns: A list of ladybug suns.
            pointGroups: A list of (x, y, z) test points or lists of (x, y, z) test
                points. Each list of test points will be converted to a
                TestPointGroup. If testPts is a single flattened list only one
                TestPointGroup will be created.
            vectorGroups: An optional list of (x, y, z) vectors. Each vector
                represents direction of corresponding point in testPts. If the
                vector is not provided (0, 0, 1) will be assigned.
            timestep: The number of timesteps per hour for sun vectors. This number
                should be smaller than 60 and divisible by 60. The default is set to
                1 such that one sun vector is generated for each hour (Default: 1).
            hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
            subFolder: Analysis subfolder for this recipe. (Default: "sunlighthours")
        """
        try:
            sunVectors = tuple(s.sunVector for s in suns if s.isDuringDay)
            hoys = tuple(s.hoy for s in suns if s.isDuringDay)
        except AttributeError:
            raise TypeError('The input is not a valid LBSun.')

        analysisGrids = cls.analysisGridsFromPointsAndVectors(pointGroups,
                                                              vectorGroups)
        return cls(sunVectors, hoys, analysisGrids, timestep, hbObjects, subFolder)

    @classmethod
    def fromLocationAndHoys(cls, location, hoys, pointGroups, vectorGroups=[],
                            timestep=1, hbObjects=None, subFolder='sunlighthour'):
        """Create sunlighthours recipe from Location and hours of year."""
        sp = Sunpath.fromLocation(location)

        suns = (sp.calculateSunFromHOY(HOY) for HOY in hoys)

        sunVectors = tuple(s.sunVector for s in suns if s.isDuringDay)

        analysisGrids = cls.analysisGridsFromPointsAndVectors(pointGroups,
                                                              vectorGroups)
        return cls(sunVectors, hoys, analysisGrids, timestep, hbObjects, subFolder)

    @classmethod
    def fromLocationAndAnalysisPeriod(
        cls, location, analysisPeriod, pointGroups, vectorGroups=None,
        hbObjects=None, subFolder='sunlighthour'
    ):
        """Create sunlighthours recipe from Location and analysis period."""
        vectorGroups = vectorGroups or ()

        sp = Sunpath.fromLocation(location)

        suns = (sp.calculateSunFromHOY(HOY) for HOY in analysisPeriod.floatHOYs)

        sunVectors = tuple(s.sunVector for s in suns if s.isDuringDay)
        hoys = tuple(s.hoy for s in suns if s.isDuringDay)

        analysisGrids = cls.analysisGridsFromPointsAndVectors(pointGroups,
                                                              vectorGroups)
        return cls(sunVectors, hoys, analysisGrids, analysisPeriod.timestep,
                   hbObjects, subFolder)

    @property
    def hoys(self):
        """Return list of hours of the year."""
        return self._hoys

    @property
    def sunVectors(self):
        """A list of ladybug sun vectors as (x, y, z) values."""
        return self._sunVectors

    @sunVectors.setter
    def sunVectors(self, vectors):
        try:
            self._sunVectors = tuple(Vector3(*v).flipped() for v in vectors
                                     if v[2] < 0)
        except TypeError:
            self._sunVectors = tuple(Vector3(v.X, v.Y, v.Z).flipped()
                                     for v in vectors if v.Z < 0)
        except IndexError:
            raise ValueError("Failed to create the sun vectors!")

        if len(self.sunVectors) != len(vectors):
            print '%d vectors with positive z value are found and removed ' \
                'from sun vectors' % (len(vectors) - len(self.sunVectors))

    @property
    def timestep(self):
        """An intger for the number of timesteps per hour for sun vectors.

        This number should be smaller than 60 and divisible by 60.
        """
        return self._timestep

    @timestep.setter
    def timestep(self, ts):
        try:
            self._timestep = int(ts)
        except TypeError:
            self._timestep = 1

        assert self._timestep != 0, 'ValueError: TimeStep cannot be 0.'

    @property
    def legendParameters(self):
        """Legend parameters for solar access analysis."""
        col = Colorset.Ecotect()
        return LegendParameters([0, 'max'], colors=col)

    def writeSuns(self, targetDir, projectName, mkdir=False):
        """Write sunlist, sun geometry and sun material files.

        Args:
            targetDir: Path to project directory (e.g. c:/ladybug)
            projectName: Project name as string. Suns will be saved as
                projectName.sun

        Returns:
            A tuple of paths to sunlist file, sun materials and sun geometries

        Exceptions:
            ValueError if targetDir doesn't exist and mkdir is False.
        """
        assert type(projectName) is str, "projectName should be a string."

        _suns = range(len(self.sunVectors))
        _mat = range(len(self.sunVectors))
        _geo = range(len(self.sunVectors))

        # create data
        for count, v in enumerate(self.sunVectors):
            _suns[count] = 'solar%d' % count
            _mat[count] = 'void light solar%d 0 0 3 1.0 1.0 1.0' % count
            _geo[count] = \
                'solar{0} source sun{0} 0 0 4 {1} {2} {3} 0.533'.format(
                    count, v.X, v.Y, v.Z)

        _sunsf = writeToFile(os.path.join(targetDir, projectName + '.sun'),
                             '\n'.join(_suns) + '\n', mkdir)
        _matf = writeToFile(os.path.join(targetDir, projectName + '_suns.mat'),
                            '\n'.join(_mat) + '\n', mkdir)
        _geof = writeToFile(os.path.join(targetDir, projectName + '_suns.rad'),
                            '\n'.join(_geo) + '\n', mkdir)

        if _sunsf and _matf and _geof:
            return _sunsf, _matf, _geof
        else:
            raise IOError('Failed to write sun vectors!')

    def write(self, targetFolder, projectName='untitled', header=True):
        """Write analysis files to target folder.

        Files for sunlight hours analysis are:
            test points <projectName.pts>: List of analysis points.
            suns file <*.sun>: list of sun sources .
            suns material file <*_suns.mat>: Radiance materials for sun sources.
            suns geometry file <*_suns.rad>: Radiance geometries for sun sources.
            material file <*.mat>: Radiance materials. Will be empty if HBObjects is
                None.
            geometry file <*.rad>: Radiance geometries. Will be empty if HBObjects is
                None.
            batch file <*.bat>: An executable batch file which has the list of commands.
                oconv [material file] [geometry file] [sun materials file] [sun
                    geometries file] > [octree file]
                rcontrib -ab 0 -ad 10000 -I -M [sunlist.txt] -dc 1 [octree file]< [pts
                    file] > [rcontrib results file]

        Args:
            targetFolder: Path to parent folder. Files will be created under
                targetFolder/gridbased. use self.subFolder to change subfolder name.
            projectName: Name of this project as a string.

        Returns:
            True in case of success.
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

        # 2.write sun files
        sunsList, sunsMat, sunsGeo = \
            self.writeSuns(projectFolder + '/sky', projectName)

        # 2.1.add sun list to modifiers
        self._radianceParameters.modFile = self.relpath(sunsList, projectFolder)
        self._radianceParameters.yDimension = self.totalPointCount

        # 3.write batch file
        if header:
            self._commands.append(self.header(projectFolder))

        # TODO(Mostapha): add windowGroups here if any!
        # # 4.1.prepare oconv
        octSceneFiles = opqfiles + glzfiles + wgsfiles + [sunsMat, sunsGeo] + \
            extrafiles.fp

        oc = Oconv(projectName)
        oc.sceneFiles = tuple(self.relpath(f, projectFolder) for f in octSceneFiles)

        # # 4.2.prepare Rcontrib
        rct = Rcontrib('result/' + projectName,
                       rcontribParameters=self._radianceParameters)
        rct.octreeFile = str(oc.outputFile)
        rct.pointsFile = self.relpath(pointsFile, projectFolder)

        batchFile = os.path.join(projectFolder, "commands.bat")
        rmtx = RGBMatrixFileToIll((str(rct.outputFile),),
                                  'result/{}.ill'.format(projectName))

        # # 4.3 write batch file
        self._commands.append(oc.toRadString())
        self._commands.append(rct.toRadString())
        self._commands.append(rmtx.toRadString())

        self._resultFiles = os.path.join(projectFolder, str(rmtx.outputFile))

        batchFile = os.path.join(projectFolder, "commands.bat")
        return writeToFile(batchFile, '\n'.join(self.commands))

    def results(self):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        print('Unloading the current values from the analysis grids.')
        for ag in self.analysisGrids:
            ag.unload()

        hours = tuple(int(self.timestep * h) for h in self.hoys)
        rf = self._resultFiles
        startLine = 0
        for count, analysisGrid in enumerate(self.analysisGrids):
            if count:
                startLine += len(self.analysisGrids[count - 1])

            analysisGrid.setValuesFromFile(
                rf, hours, startLine=startLine, header=True, checkPointCount=False,
                mode=1
            )

        return self.analysisGrids

    def toJson(self):
        """Create the solar access recipe from json.
            {
              "id": 0, // do NOT overwrite this id
              "location": null, // a honeybee location - see below
              "hoys": [], // list of hours of the year
              "surfaces": [], // list of honeybee surfaces
              "analysis_grids": [], // list of analysis grids
              "sun_vectors": []
            }
        """
        return {
            "id": 0,
            "location": None,
            "hoys": self.hoys,
            "surfaces": [srf.toJson() for srf in self.hbObjects],
            "analysis_grids": [ag.toJson() for ag in self.analysisGrids],
            "sun_vectors": [tuple(-1 * c for c in v) for v in self.sunVectors]
        }
