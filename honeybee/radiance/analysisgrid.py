"""Honeybee PointGroup and TestPointGroup."""
from __future__ import division
from ..utilcol import randomName
from ..dataoperation import matchData
from ..schedule import Schedule
from .analysispoint import AnalysisPoint

import os
from itertools import izip
from collections import namedtuple, OrderedDict


class EmptyFileError(Exception):
    """Exception for trying to load results from an empty file."""

    def __init__(self, filePath=None):
        message = ''
        if filePath:
            message = 'Failed to load the results form an empty file: {}\n' \
                'Double check inputs and outputs and make sure ' \
                'everything is run correctly.'.format(filePath)

        super(EmptyFileError, self).__init__(message)


class AnalysisGrid(object):
    """A grid of analysis points.

    Attributes:
        analysisPoints: A collection of analysis points.
    """

    __slots__ = ('_analysisPoints', '_name', '_sources', '_wgroups', '_directFiles',
                 '_totalFiles')

    def __init__(self, analysisPoints, name=None, windowGroups=None):
        """Initialize a AnalysisPointGroup.

        analysisPoints: A collection of AnalysisPoints.
        name: A unique name for this AnalysisGrid.
        windowGroups: A collection of windowGroups which contribute to this grid.
            This input is only meaningful in studies such as daylight coefficient
            and multi-phase studies that the contribution of each source will be
            calculated separately (default: None).
        """
        self.name = name
        # name of sources and their state. It's only meaningful in multi-phase daylight
        # analysis. In analysis for a single time it will be {None: [None]}
        self._sources = OrderedDict()

        if windowGroups:
            self._wgroups = tuple(wg.name for wg in windowGroups)
        else:
            self._wgroups = ()

        for ap in analysisPoints:
            assert hasattr(ap, '_dir'), \
                '{} is not an AnalysisPoint.'.format(ap)

        self._analysisPoints = analysisPoints
        self._directFiles = []  # list of results files
        self._totalFiles = []  # list of results files

    @classmethod
    def fromJson(cls, agJson):
        """Create an analysis grid from json objects."""
        analysisPoints = tuple(AnalysisPoint.fromJson(pt)
                               for pt in agJson["analysis_points"])
        return cls(analysisPoints)

    @classmethod
    def fromPointsAndVectors(cls, points, vectors=None, name=None, windowGroups=None):
        """Create an analysis grid from points and vectors.

        Args:
            points: A flatten list of (x, y ,z) points.
            vectors: An optional list of (x, y, z) for direction of test points.
                If not provided a (0, 0, 1) vector will be assigned.
        """
        vectors = vectors or ()
        points, vectors = matchData(points, vectors, (0, 0, 1))
        aps = tuple(AnalysisPoint(pt, v) for pt, v in izip(points, vectors))
        return cls(aps, name, windowGroups)

    @classmethod
    def fromFile(cls, filePath):
        """Create an analysis grid from a pts file.

        Args:
            filePath: Full path to points file
        """
        assert os.path.isfile(filePath), IOError("Can't find {}.".format(filePath))
        ap = AnalysisPoint  # load analysis point locally for better performance
        with open(filePath, 'rb') as inf:
            points = tuple(ap.fromrawValues(*l.split()) for l in inf)

        return cls(points)

    @property
    def isAnalysisGrid(self):
        """Return True for AnalysisGrid."""
        return True

    @property
    def name(self):
        """AnalysisGrid name."""
        return self._name

    @name.setter
    def name(self, n):
        self._name = n or randomName()

    @property
    def windowGroups(self):
        """A list of window group names that are related to this analysis grid."""
        return self._wgroups

    @windowGroups.setter
    def windowGroups(self, wgs):
        self._wgroups = tuple(wg.name for wg in wgs)

    @property
    def points(self):
        """A generator of points as x, y, z."""
        return (ap.location for ap in self._analysisPoints)

    @property
    def vectors(self):
        """Get generator of vectors as x, y , z."""
        return (ap.direction for ap in self._analysisPoints)

    @property
    def analysisPoints(self):
        """Return a list of analysis points."""
        return self._analysisPoints

    @property
    def sources(self):
        """Get sorted list fo sources."""
        if not self._sources:
            return self.analysisPoints[0].sources
        else:
            srcs = range(len(self._sources))
            for name, d in self._sources.iteritems():
                srcs[d['id']] = name
                return srcs

    @property
    def hasValues(self):
        """Check if this analysis grid has result values."""
        return self.analysisPoints[0].hasValues

    @property
    def hasDirectValues(self):
        """Check if direct values are available for this point.

        In point-in-time and 3phase recipes only total values are available.
        """
        return self.analysisPoints[0].hasDirectValues

    @property
    def hoys(self):
        """Return hours of the year for results if any."""
        return self.analysisPoints[0].hoys

    @property
    def isResultsPointInTime(self):
        """Return True if the grid has the results only for an hour."""
        return len(self.hoys) == 1

    @property
    def resultFiles(self):
        """Return result files as a list [[total files], [direct files]]."""
        return self._totalFiles, self._directFiles

    def addResultFiles(self, filePath, hoys, startLine=None, isDirect=False,
                       header=True, mode=0):
        """Add new result files to grid.

        Use this methods if you want to get annual metrics without loading the values
        for each point. This method is only useful for cases with no window groups and
        dynamic blind states. After adding the files you can call 'annualMetrics' method.
        """
        ResultFile = namedtuple(
            'ResultFile', ('path', 'hoys', 'startLine', 'header', 'mode'))

        inf = ResultFile(filePath, hoys, startLine, header, mode)

        if isDirect:
            self._directFiles.append(inf)
        else:
            self._totalFiles.append(inf)

    def setValues(self, hoys, values, source=None, state=None, isDirect=False):

        pass
        # assign the values to points
        for count, hourlyValues in enumerate(values):
            self.analysisPoints[count].setValues(
                hourlyValues, hoys, source, state, isDirect)

    def parseHeader(self, inf, startLine, hoys, checkPointCount=False):
        """Parse radiance matrix header."""
        # read the header
        for i in xrange(10):
            line = inf.next()
            if line[:6] == 'FORMAT':
                inf.next()  # pass empty line
                break  # done with the header!
            elif startLine == 0 and line[:5] == 'NROWS':
                pointsCount = int(line.split('=')[-1])
                if checkPointCount:
                    assert len(self._analysisPoints) == pointsCount, \
                        "Length of points [{}] must match the number " \
                        "of rows [{}].".format(
                            len(self._analysisPoints), pointsCount)

            elif startLine == 0 and line[:5] == 'NCOLS':
                hoursCount = int(line.split('=')[-1])
                if hoys:
                    assert hoursCount == len(hoys), \
                        "Number of hours [{}] must match the " \
                        "number of columns [{}]." \
                        .format(len(hoys), hoursCount)
                else:
                    hoys = xrange(0, hoursCount)

        return inf, hoys

    def setValuesFromFile(self, filePath, hoys=None, source=None, state=None,
                          startLine=None, isDirect=False, header=True,
                          checkPointCount=True, mode=0):
        """Load values for test points from a file.

        Args:
            filePath: Full file path to the result file.
            hoys: A collection of hours of the year for the results. If None the
                default will be range(0, len(results)).
            source: Name of the source.
            state: Name of the state.
            startLine: Number of start lines after the header from 0 (default: 0).
            isDirect: A Boolean to declare if the results is direct illuminance
                (default: False).
            header: A Boolean to declare if the file has header (default: True).
            mode: 0 > load the values 1 > load values as binary. Any non-zero value
                will be 1. This is useful for studies such as sunlight hours. 2 >
                load the values divided by mode number. Use this mode for daylight
                factor or radiation analysis.
        """

        if os.path.getsize(filePath) < 2:
            raise EmptyFileError(filePath)

        st = startLine or 0

        with open(filePath, 'rb') as inf:
            if header:
                inf, hoys = self.parseHeader(inf, st, hoys, checkPointCount)

            self.addResultFiles(filePath, hoys, st, isDirect, header, mode)

            for i in xrange(st):
                inf.next()

            end = len(self._analysisPoints)
            if mode == 0:
                values = (tuple(int(float(r)) for r in inf.next().split())
                          for count in xrange(end))
            elif mode == 1:
                # binary 0-1
                values = (tuple(1 if float(r) > 0 else 0 for r in inf.next().split())
                          for count in xrange(end))
            else:
                # divide values by mode (useful for daylight factor calculation)
                values = (tuple(int(float(r) / mode) for r in inf.next().split())
                          for count in xrange(end))

            # assign the values to points
            for count, hourlyValues in enumerate(values):
                self.analysisPoints[count].setValues(
                    hourlyValues, hoys, source, state, isDirect)

    def setCoupledValuesFromFile(
            self, totalFilePath, directFilePath, hoys=None, source=None, state=None,
            startLine=None, header=True, checkPointCount=True, mode=0):
        """Load direct and total values for test points from two files.

        Args:
            filePath: Full file path to the result file.
            hoys: A collection of hours of the year for the results. If None the
                default will be range(0, len(results)).
            source: Name of the source.
            state: Name of the state.
            startLine: Number of start lines after the header from 0 (default: 0).
            header: A Boolean to declare if the file has header (default: True).
            mode: 0 > load the values 1 > load values as binary. Any non-zero value
                will be 1. This is useful for studies such as sunlight hours. 2 >
                load the values divided by mode number. Use this mode for daylight
                factor or radiation analysis.
        """

        for filePath in (totalFilePath, directFilePath):
            if os.path.getsize(filePath) < 2:
                raise EmptyFileError(filePath)

        st = startLine or 0

        with open(totalFilePath, 'rb') as inf, open(directFilePath, 'rb') as dinf:
            if header:
                inf, hoys = self.parseHeader(inf, st, hoys, checkPointCount)
                dinf, hoys = self.parseHeader(dinf, st, hoys, checkPointCount)

            self.addResultFiles(totalFilePath, hoys, st, False, header, mode)
            self.addResultFiles(directFilePath, hoys, st, True, header, mode)

            for i in xrange(st):
                inf.next()
                dinf.next()

            end = len(self._analysisPoints)

            if mode == 0:
                coupledValues = (
                    tuple((int(float(r)), int(float(d))) for r, d in
                          izip(inf.next().split(), dinf.next().split()))
                    for count in xrange(end))
            elif mode == 1:
                # binary 0-1
                coupledValues = (tuple(
                    (int(float(1 if float(r) > 0 else 0)),
                     int(float(1 if float(d) > 0 else 0)))
                    for r, d in izip(inf.next().split(), dinf.next().split()))
                    for count in xrange(end))
            else:
                # divide values by mode (useful for daylight factor calculation)
                coupledValues = (
                    tuple((int(float(r) / mode), int(float(d) / mode)) for r, d in
                          izip(inf.next().split(), dinf.next().split()))
                    for count in xrange(end))

            # assign the values to points
            for count, hourlyValues in enumerate(coupledValues):
                self.analysisPoints[count].setCoupledValues(
                    hourlyValues, hoys, source, state)

    def combinedValueById(self, hoy, blindsStateIds=None):
        """Get combined value from all sources based on stateId.

        Args:
            hoy: hour of the year.
            blindsStateIds: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1.

        Returns:
            total, direct values.
        """
        if self.digitSign == 1:
            self.loadValuesFromFiles()

        return (p.combinedValueById(hoy, blindsStateIds) for p in self)

    def combinedValuesById(self, hoys=None, blindsStateIds=None):
        """Get combined value from all sources based on stateIds.

        Args:
            hoys: A collection of hours of the year.
            blindsStateIds: List of state ids for all the sources for input hoys. If you
                want a source to be removed set the state to -1.

        Returns:
            Return a generator for (total, direct) values.
        """
        if self.digitSign == 1:
            self.loadValuesFromFiles()

        return (p.combinedValueById(hoys, blindsStateIds) for p in self)

    def sumValuesById(self, hoys=None, blindsStateIds=None):
        """Get sum of value for all the hours.

        This method is mostly useful for radiation and solar access analysis.

        Args:
            hoys: A collection of hours of the year.
            blindsStateIds: List of state ids for all the sources for input hoys. If you
                want a source to be removed set the state to -1.

        Returns:
            Return a collection of sum values as (total, direct) values.
        """
        if self.digitSign == 1:
            self.loadValuesFromFiles()

        return (p.sumValuesById(hoys, blindsStateIds) for p in self)

    def maxValuesById(self, hoys=None, blindsStateIds=None):
        """Get maximum value for all the hours.

        Args:
            hoys: A collection of hours of the year.
            blindsStateIds: List of state ids for all the sources for input hoys. If you
                want a source to be removed set the state to -1.

        Returns:
            Return a tuple for sum of (total, direct) values.
        """
        if self.digitSign == 1:
            self.loadValuesFromFiles()

        return (p.maxValuesById(hoys, blindsStateIds) for p in self)

    def annualMetrics(self, DAThreshhold=None, UDIMinMax=None, blindsStateIds=None,
                      occSchedule=None):
        """Calculate annual metrics.

        Daylight autonomy, continious daylight autonomy and useful daylight illuminance.

        Args:
            DAThreshhold: Threshhold for daylight autonomy in lux (default: 300).
            UDIMinMax: A tuple of min, max value for useful daylight illuminance
                (default: (100, 3000)).
            blindsStateIds: List of state ids for all the sources for input hoys. If you
                want a source to be removed set the state to -1.
            occSchedule: An annual occupancy schedule.

        Returns:
            Daylight autonomy, Continious daylight autonomy, Useful daylight illuminance,
            Less than UDI, More than UDI
        """
        resultsLoaded = True
        if not self.hasValues and not self.resultFiles[0]:
            raise ValueError('No values are assigned to this analysis grid.')
        elif not self.hasValues:
            # results are not loaded but are available
            assert len(self.resultFiles[0]) == 1, \
                ValueError(
                    'Annual recipe can currently only handle '
                    'a single merged result file.'
            )
            resultsLoaded = False
            print('Loading the results from result files.')

        res = ([], [], [], [], [])

        DAThreshhold = DAThreshhold or 300.0
        UDIMinMax = UDIMinMax or (100, 3000)
        hoys = self.hoys
        occSchedule = occSchedule or Schedule.fromWorkdayHours()

        if resultsLoaded:
            blindsStateIds = blindsStateIds or [[0] * len(self.sources)] * len(hoys)

            for sensor in self.analysisPoints:
                for c, r in enumerate(sensor.annualMetrics(DAThreshhold,
                                                           UDIMinMax,
                                                           blindsStateIds,
                                                           occSchedule
                                                           )):
                    res[c].append(r)
        else:
            # This is a method for annual recipe to load the results line by line
            # which unlike the other method doesn't load all the values to the memory
            # at once.
            blindsStateIds = [[0] * len(self.sources)] * len(hoys)
            calculateAnnualMetrics = self.analysisPoints[0]._calculateAnnualMetrics

            for fileData in self.resultFiles[0]:
                filePath, hoys, startLine, header, mode = fileData

                # read the results line by line and caluclate the values
                if os.path.getsize(filePath) < 2:
                    raise EmptyFileError(filePath)

                assert mode == 0, \
                    TypeError(
                        'Annual results can only be calculated from '
                        'illuminance studies.')

                st = startLine or 0

                with open(filePath, 'rb') as inf:
                    if header:
                        inf, _ = self.parseHeader(inf, st, hoys, False)

                    for i in xrange(st):
                        inf.next()

                    end = len(self._analysisPoints)

                    # load one line at a time
                    for count in xrange(end):
                        values = (int(float(r)) for r in inf.next().split())
                        for c, r in enumerate(
                            calculateAnnualMetrics(
                                values, hoys, DAThreshhold, UDIMinMax,
                                blindsStateIds, occSchedule)):

                            res[c].append(r)

        return res

    def spatialDaylightAutonomy(self, DAThreshhold=None, blindsStateIds=None,
                                occSchedule=None, targetArea=None):
        """Calculate Spatial Daylight Autonomy (sDA).

        Args:
            targetArea: Minimum target area percentage for this grid (default: 50)
        """
        resultsLoaded = True
        if not self.hasValues and not self.resultFiles[0]:
            raise ValueError('No values are assigned to this analysis grid.')
        elif not self.hasValues:
            # results are not loaded but are available
            assert len(self.resultFiles[0]) == 1, \
                ValueError(
                    'Annual recipe can currently only handle '
                    'a single merged result file.'
            )
            resultsLoaded = False
            print('Loading the results from result files.')

        DAThreshhold = DAThreshhold or 300.0
        hoys = self.hoys
        occSchedule = occSchedule or Schedule.fromWorkdayHours()

        if resultsLoaded:
            blindsStateIds = blindsStateIds or [[0] * len(self.sources)] * len(hoys)

            # get the annual results for each sensor
            hourlyResults = (
                sensor.combinedValuesById(hoys, blindsStateIds)
                for sensor in self.analysisPoints
            )
        else:
            blindsStateIds = [[0] * len(self.sources)] * len(hoys)
            for fileData in self.resultFiles[0]:
                filePath, hoys, startLine, header, mode = fileData

                # read the results line by line and caluclate the values
                if os.path.getsize(filePath) < 2:
                    raise EmptyFileError(filePath)

                assert mode == 0, \
                    TypeError(
                        'Annual results can only be calculated from '
                        'illuminance studies.')

                st = startLine or 0

                with open(filePath, 'rb') as inf:
                    if header:
                        inf, _ = self.parseHeader(inf, st, hoys, False)

                    for i in xrange(st):
                        inf.next()

                    end = len(self._analysisPoints)
                    hourlyResults = \
                        tuple(tuple((int(float(r)), None) for r in inf.next().split())
                              for count in xrange(end))

        # iterate through the results
        # find minimum number of points to meet the targetArea
        targetArea = targetArea * len(self.analysisPoints) / 100 or \
            0.50 * len(self.analysisPoints)
        # change target area to an integer to enhance the performance in the loop
        target = int(targetArea) if int(targetArea) != targetArea \
            else int(targetArea - 1)

        metHours = 0
        problematicHours = []
        for hr, hrv in izip(hoys, izip(*hourlyResults)):
            if hr not in occSchedule:
                continue
            count = sum(1 if res[0] > DAThreshhold else 0 for res in hrv)
            if count > target:
                metHours += 1
            else:
                problematicHours.append(hr)

        return 100 * metHours / len(occSchedule.occupiedHours), problematicHours

    def annualSolarExposure(self, threshhold=None, blindsStateIds=None,
                            occSchedule=None, targetHours=None, targetArea=None):
        """Annual Solar Exposure (ASE)

        As per IES-LM-83-12 ASE is the percent of sensors that are
        found to be exposed to more than 1000lux of direct sunlight for
        more than 250hrs per year. For LEED credits No more than 10% of
        the points in the grid should fail this measure.

        Args:
            threshhold: Threshhold for for solar exposure in lux (default: 1000).
            blindsStateIds: List of state ids for all the sources for input hoys.
                If you want a source to be removed set the state to -1. ASE must
                be calculated without dynamic blinds but you can use this option
                to study the effect of different blind states.
            occSchedule: An annual occupancy schedule.
            targetHours: Minimum targe hours for each point (default: 250).
            targetArea: Minimum target area percentage for this grid (default: 10)

        Returns:
            Success as a Boolean, ASE values for each point, Percentage area,
            Problematic points, Problematic hours for each point
        """
        resultsLoaded = True
        if not self.hasDirectValues and not self.resultFiles[1]:
            raise ValueError(
                'Direct values are not available to calculate ASE.\nIn most of the cases'
                ' this is because you are using a point in time recipe or the three-'
                'phase recipe. You should use one of the daylight coefficient based '
                'recipes or the 5 phase recipe instead.')
        elif not self.hasDirectValues:
            # results are not loaded but are available
            assert len(self.resultFiles[1]) == 1, \
                ValueError(
                    'Annual recipe can currently only handle '
                    'a single merged result file.'
            )
            resultsLoaded = False
            print('Loading the results from result files.')

        res = ([], [], [])
        threshhold = threshhold or 1000
        targetHours = targetHours or 250
        targetArea = targetArea or 10
        hoys = self.hoys
        occSchedule = occSchedule or set(hoys)

        if resultsLoaded:
            blindsStateIds = blindsStateIds or [[0] * len(self.sources)] * len(hoys)

            for sensor in self.analysisPoints:
                for c, r in enumerate(sensor.annualSolarExposure(threshhold,
                                                                 blindsStateIds,
                                                                 occSchedule,
                                                                 targetHours
                                                                 )):
                    res[c].append(r)
        else:
            # This is a method for annual recipe to load the results line by line
            # which unlike the other method doesn't load all the values to the memory
            # at once.
            blindsStateIds = [[0] * len(self.sources)] * len(hoys)
            calculateAnnualSolarExposure = \
                self.analysisPoints[0]._calculateAnnualSolarExposure

            for fileData in self.resultFiles[1]:
                filePath, hoys, startLine, header, mode = fileData

                # read the results line by line and caluclate the values
                if os.path.getsize(filePath) < 2:
                    raise EmptyFileError(filePath)

                assert mode == 0, \
                    TypeError(
                        'Annual results can only be calculated from '
                        'illuminance studies.')

                st = startLine or 0

                with open(filePath, 'rb') as inf:
                    if header:
                        inf, _ = self.parseHeader(inf, st, hoys, False)

                    for i in xrange(st):
                        inf.next()

                    end = len(self._analysisPoints)

                    # load one line at a time
                    for count in xrange(end):
                        values = (int(float(r)) for r in inf.next().split())
                        for c, r in enumerate(
                            calculateAnnualSolarExposure(
                                values, hoys, threshhold, blindsStateIds, occSchedule,
                                targetHours)):

                            res[c].append(r)

        # calculate ASE for the grid
        ap = self.analysisPoints  # create a local copy of points for better performance
        problematicPointCount = 0
        problematicPoints = []
        problematicHours = []
        aseValues = []
        for i, (success, ase, pHours) in enumerate(izip(*res)):
            aseValues.append(ase)  # collect annual ASE values for each point
            if success:
                continue
            problematicPointCount += 1
            problematicPoints.append(ap[i])
            problematicHours.append(pHours)

        perProblematic = 100 * problematicPointCount / len(ap)
        return perProblematic < targetArea, aseValues, perProblematic, \
            problematicPoints, problematicHours

    def parseBlindStates(self, blindsStateIds):
        """Parse input blind states.

        The method tries to convert each state to a tuple of a list. Use this method
        to parse the input from plugins.

        Args:
            blindsStateIds: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1. If not provided
                a longest combination of states from sources (window groups) will
                be used. Length of each item in states should be equal to number
                of sources.
        """
        return self.analysisPoints[0].parseBlindStates(blindsStateIds)

    def loadValuesFromFiles(self):
        """Load grid values from self.resultFiles."""
        # remove old results
        for ap in self._analysisPoints:
            ap._sources = OrderedDict()
            ap._values = []
        rFiles = self.resultFiles[0][:]
        dFiles = self.resultFiles[1][:]
        self._totalFiles = []
        self._directFiles = []
        # pass
        if rFiles and dFiles:
            # both results are available
            for rf, df in izip(rFiles, dFiles):
                rfPath, hoys, startLine, header, mode = rf
                dfPath, hoys, startLine, header, mode = df
                fn = os.path.split(rfPath)[-1][:-4].split("..")
                source = fn[-2]
                state = fn[-1]
                print(
                    '\nloading total and direct results for {} AnalysisGrid'
                    ' from {}::{}\n{}\n{}\n'.format(
                        self.name, source, state, rfPath, dfPath))
                self.setCoupledValuesFromFile(
                    rfPath, dfPath, hoys, source, state, startLine, header,
                    False, mode
                )
        elif rFiles:
            for rf in rFiles:
                rfPath, hoys, startLine, header, mode = rf
                fn = os.path.split(rfPath)[-1][:-4].split("..")
                source = fn[-2]
                state = fn[-1]
                print('\nloading the results for {} AnalysisGrid form {}::{}\n{}\n'
                      .format(self.name, source, state, rfPath))
                self.setValuesFromFile(
                    rf, hoys, source, state, startLine, isDirect=False,
                    header=header, checkPointCount=False, mode=mode
                )
        elif dFiles:
            for rf in dFiles:
                rfPath, hoys, startLine, header, mode = rf
                fn = os.path.split(rfPath)[-1][:-4].split("..")
                source = fn[-2]
                state = fn[-1]
                print('\nloading the results for {} AnalysisGrid form {}::{}\n{}\n'
                      .format(self.name, source, state, rfPath))
                self.setValuesFromFile(
                    rf, hoys, source, state, startLine, isDirect=True,
                    header=header, checkPointCount=False, mode=mode
                )

    def unload(self):
        """Remove all the sources and values from analysisPoints."""
        self._totalFiles = []
        self._directFiles = []

        for ap in self._analysisPoints:
            ap._sources = OrderedDict()
            ap._values = []

    def duplicate(self):
        """Duplicate AnalysisGrid."""
        aps = tuple(ap.duplicate() for ap in self._analysisPoints)
        dup = AnalysisGrid(aps, self._name)
        dup._sources = aps[0]._sources
        dup._wgroups = self._wgroups
        return dup

    def toRadString(self):
        """Return analysis points group as a Radiance string."""
        return "\n".join((ap.toRadString() for ap in self._analysisPoints))

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def toJson(self):
        """Create an analysis grid from json objects."""
        analysisPoints = [ap.toJson() for ap in self.analysisPoints]
        return {"analysis_points": analysisPoints}

    def __add__(self, other):
        """Add two analysis grids and create a new one.

        This method won't duplicate the analysis points.
        """
        assert isinstance(other, AnalysisGrid), \
            TypeError('Expected an AnalysisGrid not {}.'.format(type(other)))

        assert self.hoys == other.hoys, \
            ValueError('Two analysis grid must have the same hoys.')

        if not self.hasValues:
            sources = self._sources.update(other._sources)
        else:
            assert self._sources == other._sources, \
                ValueError(
                    'Two analysis grid with values must have the same windowGroups.'
                )
            sources = self._sources

        points = self.analysisPoints + other.analysisPoints
        name = '{}+{}'.format(self.name, other.name)
        addition = AnalysisGrid(points, name)
        addition._sources = sources

        return addition

    def __len__(self):
        """Number of points in this group."""
        return len(self._analysisPoints)

    def __getitem__(self, index):
        """Get value for an index."""
        return self._analysisPoints[index]

    def __iter__(self):
        """Iterate points."""
        return iter(self._analysisPoints)

    def __str__(self):
        """String repr."""
        return self.toRadString()

    @property
    def digitSign(self):
        if not self.hasValues:
            if len(self.resultFiles[0]) + len(self.resultFiles[1]) == 0:
                # only x, y, z datat is available
                return 0
            else:
                # results are available but are not loaded yet
                return 1
        elif self.isResultsPointInTime:
            # results is loaded for a single hour
            return 2
        else:
            # results is loaded for multiple hours
            return 3

    @property
    def _sign(self):
        if not self.hasValues:
            if len(self.resultFiles[0]) + len(self.resultFiles[1]) == 0:
                # only x, y, z datat is available
                return '[.]'
            else:
                # results are available but are not loaded yet
                return '[/]'
        elif self.isResultsPointInTime:
            # results is loaded for a single hour
            return '[+]'
        else:
            # results is loaded for multiple hours
            return '[*]'

    def __repr__(self):
        """Return analysis points and directions."""
        return 'AnalysisGrid::{}::#{}::{}'.format(
            self._name, len(self._analysisPoints), self._sign
        )
