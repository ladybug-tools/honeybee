"""Honeybee PointGroup and TestPointGroup."""
from ..vectormath.euclid import Point3, Vector3
from ..dataoperation import matchData

from itertools import izip


# TODO(mostapha): Implement values, UDI, DA, etc.
class AnalysisPoint(object):
    """A radiance analysis point.

    Attributes:
        location: Location of analysis points as (x, y, z).
        direction: Direction of analysis point as (x, y, z).
        values: List of values for this analysis point.
        sources:
        states:
    """

    __slots__ = ('_loc', '_dir', '_values', '_sources')

    def __init__(self, location, direction, values=None, sources=None):
        """Create an analysis point."""
        self.location = location
        self.direction = direction
        self._sources = sources
        self._values = values

    @property
    def location(self):
        """Location of analysis points as Point3."""
        return self._loc

    @location.setter
    def location(self, location):
        try:
            self._loc = Point3(*location)
        except TypeError:
            raise TypeError(
                'Failed to convert {} to location.\n'
                'location should be a list or a tuple with 3 values.'.format(location))

    @property
    def direction(self):
        """Direction of analysis points as Point3."""
        return self._dir

    @direction.setter
    def direction(self, direction):
        try:
            self._dir = Vector3(*direction)
        except TypeError:
            raise TypeError(
                'Failed to convert {} to direction.\n'
                'location should be a list or a tuple with 3 values.'.format(direction))

    @property
    def usefulDaylightIlluminance(self):
        """Get UDI for this analysis point."""
        raise NotImplementedError()

    @property
    def daylightAutonomy(self):
        """Get DA for this analysis point."""
        raise NotImplementedError()

    def toRadString(self):
        """Return Radiance string for a test point."""
        return "%s %s" % (self.location, self.direction)

    def __repr__(self):
        """Print and analysis point."""
        return self.toRadString()


class AnalysisGrid(object):
    """A grid of analysis points.

    Attributes:
        analysisPoints: A collection of analysis points.
    """

    __slots__ = ('_analysisPoints')

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

    @property
    def isAnalysisGrid(self):
        """Return True for AnalysisGrid."""
        return True

    @property
    def points(self):
        """A list of points as x, y, z."""
        return (ap.location for ap in self._analysisPoints)

    @property
    def vectors(self):
        """Get list of vectors as x, y , z."""
        return (ap.direction for ap in self._analysisPoints)

    @property
    def analysisPoints(self):
        """Return a list of analysis points."""
        return self._analysisPoints

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
        return 'AnalysisGrid::#AnalysisPoints::{}'.format(len(self._analysisPoints))
