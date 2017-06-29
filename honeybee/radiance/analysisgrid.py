"""Honeybee PointGroup and TestPointGroup."""
from __future__ import division
from ..utilcol import randomName
from ..dataoperation import matchData
from .analysispoint import AnalysisPoint

import os
from itertools import izip


# TODO(mostapha): Implement sources from windowGroups
class AnalysisGrid(object):
    """A grid of analysis points.

    Attributes:
        analysisPoints: A collection of analysis points.
    """

    __slots__ = ('_analysisPoints', '_name', '_sources')

    # TODO(mostapha): Add sources.
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
        self._sources = {}

        if windowGroups:
            raise NotImplementedError('windowGroups are not implemented.')

        for ap in analysisPoints:
            assert isinstance(ap, AnalysisPoint), '{} is not an AnalysisPoint.'
        self._analysisPoints = analysisPoints

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
        if self._sources == {}:
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
        """Check if direct values are loaded for this point.

        In some cases and based on the recipe only total values are available.
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

    def setValues(self, hoys, values, source=None, state=None, isDirect=False):

        pass
        # assign the values to points
        for count, hourlyValues in enumerate(values):
            self.analysisPoints[count].setValues(
                hourlyValues, hoys, source, state, isDirect)

    def setValuesFromFile(self, filePath, hoys=None, source=None, state=None,
                          startLine=None, isDirect=False, header=True):
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
        """
        with open(filePath, 'rb') as inf:
            if header:
                # read the header
                for i in xrange(7):
                    if startLine == 0 and i == 2:
                        pointsCount = int(inf.next().split('=')[-1])
                        assert len(self._analysisPoints) == pointsCount, \
                            "Length of points [%d] doesn't match length " \
                            "of the results [%d]." \
                            .format(len(self._analysisPoints), pointsCount)
                    elif startLine == 0 and i == 3:
                        hoursCount = int(inf.next().split('=')[-1])
                        if hoys:
                            assert hoursCount == len(hoys), \
                                "Number of hours [%d] doesn't match length " \
                                "of the results [%d]." \
                                .format(len(hoys), hoursCount)
                        else:
                            hoys = xrange(0, hoursCount)
                    else:
                        inf.next()

            st = startLine or 0
            for i in xrange(st):
                inf.next()

            end = len(self._analysisPoints)
            values = (tuple(int(float(r)) for r in inf.next().split())
                      for count in xrange(end))

            # assign the values to points
            for count, hourlyValues in enumerate(values):
                self.analysisPoints[count].setValues(
                    hourlyValues, hoys, source, state, isDirect)

    def setCoupledValuesFromFile(self, totalFilePath, directFilePath, source=None,
                                 state=None):
        pass

    def annualMetrics(self, DAThreshhold=None, UDIMinMax=None, blindsStateIds=None,
                      occSchedule=None):
        """Calculate annual metrics.

        Daylight autonomy, continious daylight autonomy and useful daylight illuminance.

        Args:
            DAThreshhold: Threshhold for daylight autonomy in lux (default: 300).
            UDIMinMax: A tuple of min, max value for useful daylight illuminance
                (default: (100, 2000)).
            blindsStateIds: List of state ids for all the sources for input hoys. If you
                want a source to be removed set the state to -1.
            occSchedule: An annual occupancy schedule.

        Returns:
            Daylight autonomy, Continious daylight autonomy, Useful daylight illuminance,
            Less than UDI, More than UDI
        """
        if not self.hasValues:
            raise ValueError('No values are assigned to this analysis grid.')

        res = ([], [], [], [], [])

        DAThreshhold = DAThreshhold or 300.0
        UDIMinMax = UDIMinMax or (100, 2000)
        hours = self.hoys
        occSchedule = occSchedule or set(hours)
        blindsStateIds = blindsStateIds or [[0] * len(self.sources)] * len(hours)

        for sensor in self.analysisPoints:
            for c, r in enumerate(sensor.annualMetrics(DAThreshhold,
                                                       UDIMinMax,
                                                       blindsStateIds,
                                                       occSchedule
                                                       )):
                res[c].append(r)

        return res

    def spatialDaylightAutonomy(self, DAThreshhold=None, blindsStateIds=None,
                                occSchedule=None, targetArea=None):
        """Calculate Spatial Daylight Autonomy (sDA).

        Args:
            targetArea: Minimum target area percentage for this grid (default: 55)
        """
        if not self.hasValues:
            raise ValueError('No values are assigned to this analysis grid.')

        DAThreshhold = DAThreshhold or 300.0
        hours = self.hoys
        occSchedule = occSchedule or set(hours)
        blindsStateIds = blindsStateIds or [[0] * len(self.sources)] * len(hours)

        # get the annual results for each sensor
        hourlyResults = (
            sensor.combinedValuesById(hours, blindsStateIds)
            for sensor in self.analysisPoints
        )

        # iterate through the results
        # find minimum number of points to meet the targetArea
        targetArea = targetArea * len(self.analysisPoints) / 100 or \
            0.55 * len(self.analysisPoints)
        # change target area to an integer to enhance the performance in the loop
        target = int(targetArea) if int(targetArea) != targetArea \
            else int(targetArea - 1)
        metHours = 0
        problematicHours = []
        for hr, hrv in izip(hours, izip(*hourlyResults)):
            if hr not in occSchedule:
                continue
            count = sum(1 if res[0] > DAThreshhold else 0 for res in hrv)
            if count > target:
                metHours += 1
            else:
                problematicHours.append(hr)

        return metHours / len(hours), problematicHours

    def annualSolarExposure(self, threshhold=None, blindsStateIds=None,
                            occSchedule=None, targetHours=None, targetArea=None):
        """Annual Solar Exposure (ASE)

        As per IES-LM-83-12 ASE is the percent of sensors that are
        found to be exposed to more than 1000lux of direct sunlight for
        more than 250hrs per year. For LEED credits No more than 10% of
        the points in the grid fail this measure.

        Args:
            threshhold: Threshhold for daylight autonomy in lux (default: 1000).
            blindsStateIds: List of state ids for all the sources for input hoys.
                If you want a source to be removed set the state to -1. ASE must
                be calculated without dynamic blinds but you can use this option
                to study the effect of different blind states.
            occSchedule: An annual occupancy schedule.
            targetHours: Minimum targe hours for each point (default: 250).
            targetArea: Minimum target area percentage for this grid (default: 10)

        Returns:
            Success as a Boolean, Percentage area, Problematic points,
            Problematic hours for each point
        """
        if not self.hasDirectValues:
            raise ValueError('Direct values are not loaded to calculate ASE.')

        res = ([], [], [])
        threshhold = threshhold or 1000
        targetHours = targetHours or 250
        targetArea = targetArea or 10
        hours = self.hoys
        occSchedule = occSchedule or set(hours)
        blindsStateIds = blindsStateIds or [[0] * len(self.sources)] * len(hours)

        for sensor in self.analysisPoints:
            for c, r in enumerate(sensor.annualSolarExposure(threshhold,
                                                             blindsStateIds,
                                                             occSchedule,
                                                             targetHours
                                                             )):
                res[c].append(r)

        # calculate ASE for the grid
        ap = self.analysisPoints  # create a local copy of points for better performance
        problematicPointCount = 0
        problematicPoints = []
        problematicHours = []
        for i, (success, _, pHours) in enumerate(izip(*res)):
            if success:
                continue

            problematicPointCount += 1
            problematicPoints.append(ap[i])
            problematicHours.append(pHours)

        return 100 * problematicPointCount / len(ap) < targetArea, \
            100 * problematicPointCount / len(ap), problematicPoints, \
            problematicHours

    def duplicate(self):
        """Duplicate AnalysisGrid."""
        dup = AnalysisGrid(self._analysisPoints, self._name)
        dup._sources = self.sources
        return dup

    def toRadString(self):
        """Return analysis points group as a Radiance string."""
        return "\n".join((ap.toRadString() for ap in self._analysisPoints))

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

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
    def _sign(self):
        if not self.hasValues:
            return '[.]'
        elif self.isResultsPointInTime:
            return '[+]'
        else:
            return '[*]'

    def __repr__(self):
        """Return analysis points and directions."""
        return 'AnalysisGrid::{}::#{}::{}'.format(
            self._name, len(self._analysisPoints), self._sign
        )
