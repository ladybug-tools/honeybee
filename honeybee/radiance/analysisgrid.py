"""Honeybee PointGroup and TestPointGroup."""
from __future__ import division
from ..dataoperation import matchData
from analysispoint import AnalysisPoint

import os
from itertools import izip


class AnalysisGrid(object):
    """A grid of analysis points.

    Attributes:
        analysisPoints: A collection of analysis points.
    """

    __slots__ = ('_analysisPoints')

    # TODO(mostapha): Add sources.
    def __init__(self, analysisPoints):
        """Initialize a AnalysisPointGroup."""
        for ap in analysisPoints:
            assert isinstance(ap, AnalysisPoint), '{} is not an AnalysisPoint.'
        self._analysisPoints = analysisPoints

    @classmethod
    def fromPointsAndVectors(cls, points, vectors=None):
        """Create an analysis grid from points and vectors.

        Args:
            points: A flatten list of (x, y ,z) points.
            vectors: An optional list of (x, y, z) for direction of test points.
                If not provided a (0, 0, 1) vector will be assigned.
        """
        vectors = vectors or ()
        points, vectors = matchData(points, vectors, (0, 0, 1))
        aps = tuple(AnalysisPoint(pt, v) for pt, v in izip(points, vectors))
        return cls(aps)

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

    def setValues(self, hoys, values, source=None, state=None, isDirect=False):

        pass
        # assign the values to points
        for count, hourlyValues in enumerate(values):
            self.analysisPoints[count].setValues(
                hourlyValues, hoys, source, state, isDirect)

    def setValuesFromFile(self, filePath, hoys=None, source=None, state=None,
                          isDirect=False):
        """Load values for test points from a file.

        Args:
            filePath: Full file path to the result file.
            hoys: A collection of hours of the year for the results. If None the
                default will be range(0, len(results)).
            source: Name of the source.
            state: Name of the state.
        """
        with open(filePath, 'rb') as inf:
            # read the header
            for i in xrange(7):
                if i == 2:
                    pointsCount = int(inf.next().split('=')[-1])
                    assert len(self._analysisPoints) == pointsCount, \
                        "Length of points [%d] doesn't match length of the results [%d]." \
                        .format(len(self._analysisPoints), pointsCount)
                elif i == 3:
                    hoursCount = int(inf.next().split('=')[-1])
                    if hoys:
                        assert hoursCount == len(hoys), \
                            "Number of hours [%d] doesn't match length of the results [%d]." \
                            .format(len(hoys), hoursCount)
                    else:
                        hoys = xrange(0, hoursCount)
                else:
                    inf.next()

            values = (tuple(int(float(r)) for r in line.split()) for line in inf)

            # assign the values to points
            for count, hourlyValues in enumerate(values):
                self.analysisPoints[count].setValues(
                    hourlyValues, hoys, source, state, isDirect)

    def setCoupledValuesFromFile(self, totalFilePath, directFilePath, source=None,
                                 state=None):
        pass

    def toRadString(self):
        """Return analysis points group as a Radiance string."""
        return "\n".join((ap.toRadString() for ap in self._analysisPoints))

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

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

    def __repr__(self):
        """Return analysis points and directions."""
        return 'AnalysisGrid::#{}'.format(len(self._analysisPoints))
