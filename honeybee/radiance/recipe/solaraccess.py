from ._gridbasedbase import GenericGridBased
from ..postprocess.sunlighthourresults import LoadSunlighthoursResults
from ..parameters.rcontrib import RcontribParameters
from ..command.oconv import Oconv
from ..command.rcontrib import Rcontrib
from ...futil import writeToFile
from ...vectormath.euclid import Vector3

from ladybug.sunpath import Sunpath
from ladybug.legendparameters import LegendParameters
from ladybug.color import Colorset

import os


class SolarAccess(GenericGridBased):
    """Solar access recipe.

    This class calculates number of sunlight hours for a group of test points.

    Attributes:
        sunVectors: A list of ladybug sun vectors as (x, y, z) values. Z value
            for sun vectors should be negative (coming from sun toward earth)
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

    def __init__(self, sunVectors, analysisGrids, timestep=1, hbObjects=None,
                 subFolder='solaraccess'):
        """Create sunlighthours recipe."""
        GenericGridBased.__init__(
            self, analysisGrids, hbObjects, subFolder
        )

        self.sunVectors = sunVectors
        self.timestep = timestep

        self._radianceParameters = RcontribParameters()
        self._radianceParameters.irradianceCalc = True
        self._radianceParameters.ambientBounces = 0
        self._radianceParameters.directCertainty = 1
        self._radianceParameters.directThreshold = 0
        self._radianceParameters.directJitter = 0

        # create a result loader to load the results once the analysis is done.
        self.loader = LoadSunlighthoursResults(self.timestep, self.resultsFile)

    def fromPointsAndVectors(cls, sunVectors, pointGroups, vectorGroups=[],
                             timestep=1, hbObjects=None, subFolder='sunlighthour'):
        """Create sunlighthours recipe from points and vectors.

        Args:
            sunVectors: A list of ladybug sun vectors as (x, y, z) values. Z value
                for sun vectors should be negative (coming from sun toward earth)
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
        return cls(sunVectors, analysisGrids, timestep, hbObjects, subFolder)

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
        except AttributeError:
            raise TypeError('The input is not a valid LBSun.')

        analysisGrids = cls.analysisGridsFromPointsAndVectors(pointGroups,
                                                              vectorGroups)
        return cls(sunVectors, analysisGrids, timestep, hbObjects, subFolder)

    @classmethod
    def fromLocationAndHoys(cls, location, HOYs, pointGroups, vectorGroups=[],
                            timestep=1, hbObjects=None, subFolder='sunlighthour'):
        """Create sunlighthours recipe from Location and hours of year."""
        sp = Sunpath.fromLocation(location)

        suns = (sp.calculateSunFromHOY(HOY) for HOY in HOYs)

        sunVectors = tuple(s.sunVector for s in suns if s.isDuringDay)

        analysisGrids = cls.analysisGridsFromPointsAndVectors(pointGroups,
                                                              vectorGroups)
        return cls(sunVectors, analysisGrids, timestep, hbObjects, subFolder)

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

        analysisGrids = cls.analysisGridsFromPointsAndVectors(pointGroups,
                                                              vectorGroups)
        return cls(sunVectors, analysisGrids, analysisPeriod.timestep, hbObjects,
                   subFolder)

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

    def writeSunsToFile(self, targetDir, projectName, mkdir=False):
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

    # TODO: Add path to PATH and use relative path in batch files
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
        sceneFiles = super(
            GenericGridBased, self).populateSubFolders(
                targetFolder, projectName)

        # 1.write points
        pointsFile = self.writePointsToFile(sceneFiles.path, projectName)

        # 2.write sun files
        sunsList, sunsMat, sunsGeo = self.writeSunsToFile(
            sceneFiles.path + '\\skies', projectName)

        # 2.1.add sun list to modifiers
        self._radianceParameters.modFile = self.relpath(sunsList, sceneFiles.path)

        # 3.write batch file
        self.commands = []
        self.resultsFile = []

        if header:
            self.commands.append(self.header(sceneFiles.path))

        # # 4.1.prepare oconv
        octSceneFiles = [sceneFiles.matFile, sceneFiles.geoFile, sunsMat, sunsGeo] + \
            sceneFiles.sceneMatFiles + sceneFiles.sceneRadFiles + \
            sceneFiles.sceneOctFiles

        oc = Oconv(projectName)
        oc.sceneFiles = tuple(self.relpath(f, sceneFiles.path)
                              for f in octSceneFiles)

        # # 4.2.prepare Rcontrib
        rct = Rcontrib('results\\' + projectName,
                       rcontribParameters=self._radianceParameters)
        rct.octreeFile = str(oc.outputFile)
        rct.pointsFile = self.relpath(pointsFile, sceneFiles.path)

        # # 4.3 write batch file
        self.commands.append(oc.toRadString())
        self.commands.append(rct.toRadString())
        batchFile = os.path.join(sceneFiles.path, "commands.bat")

        writeToFile(batchFile, '\n'.join(self.commands))

        self.resultsFile = (os.path.join(sceneFiles.path, str(rct.outputFile)),)

        print 'Files are written to: %s' % sceneFiles.path
        return batchFile

    def results(self, flattenResults=True):
        """Return results for this analysis."""
        assert self.isCalculated, \
            'You haven not run the Recipe yet. Use self.run ' + \
            'to run the analysis before loading the results.'

        self.loader.timestep = self.timestep
        self.loader.resultFiles = self.resultsFile
        return self.loader.results
