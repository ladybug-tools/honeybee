"""Honeybee PointGroup and TestPointGroup."""
from vectormath.euclid import Point3, Vector3
from dataoperation import flattenTupleList


class AnalysisPoint(object):
    """An analysis point.

    Attributes:
        location: Location of analysis points as Point3
        direction: Direction of analysis point as Vector3
    """

    def __init__(self, location, direction):
        """Create an analysis point."""
        self.location = location
        self.direction = direction

    @property
    def location(self):
        """Location of analysis points as Point3."""
        return self.__loc

    @location.setter
    def location(self, location):
        assert isinstance(location, Point3), "location should be a Piont3."
        self.__loc = location

    @property
    def direction(self):
        """Direction of analysis points as Point3."""
        return self.__dir

    @direction.setter
    def direction(self, direction):
        assert isinstance(direction, Vector3), "Direction should be a Vector3."
        self.__dir = direction

    def toRadString(self):
        """Return Radiance string for a test point."""
        return "%s %s" % (self.location, self.direction)

    def __repr__(self):
        """Print and analysis point."""
        return self.toRadString()


class PointGroup(object):
    """A group of falttened points.

    Attributes:
        points: A list of points as (x, y ,z)
    """

    def __init__(self, points):
        """Initialize a PointGroup."""
        self.__pointsCount = 0

        self.points = points
        """A list of points as x, y, z."""

    @property
    def points(self):
        """A list of points as x, y, z."""
        return self.__pts

    # TODO: Try to keep them as a generator. Even after overwriting __iter__
    # once I iteate through the objects it is empty!
    @points.setter
    def points(self, points):
        # convert tuple points to point objects
        self.__pts = list(self.__tuplesToPoints(flattenTupleList(points)))

    @property
    def pointsCount(self):
        """Number of points in point group."""
        return self.__pointsCount

    def __tuplesToPoints(self, pts):
        """Conver a list of tuples to Points.

        Args:
            pts: A list of pts and x, y, z values
        """
        self.__pointsCount = 0
        for pt in pts:
            self.__pointsCount += 1
            try:
                yield Point3(*pt)
            except:
                self.__pointsCount -= 1
                if not pt:
                    print "None input point found and removed from the list."
                else:
                    print "Failed to convert %s to a point." % str(pt)

    def sortPointsClockWise(self, normal):
        """Sort points clockwise based on an input normal."""
        raise NotImplementedError

    def __len__(self):
        """Number of points in this group."""
        return self.pointsCount

    def __getitem__(self, index):
        """Get value for an index."""
        return self.points[index]

    def __iter__(self):
        """Iterate points."""
        return iter(self.points)

    def __repr__(self):
        """Return list of points."""
        return str(self.points)


class AnalysisPointGroup(PointGroup):
    """A group of falttened analysis points and point vectors.

    Attributes:
        points: A list of (x, y ,z) points.
        vectors: An optional list of (x, y, z) for direction of test points.
            If not provided a (0, 0, 1) vector will be assigned.
    """

    def __init__(self, points, vectors=[]):
        """Initialize a AnalysisPointGroup."""
        self.__analysisPoints = []
        PointGroup.__init__(self, points)
        self.vectors = vectors

    @property
    def vectors(self):
        """Get and set vectors.

        If vector is not provided for a point a (0, 0, 1) vector will be assigned.
        """
        return self.__vectors

    @vectors.setter
    def vectors(self, vectors):
        try:
            __vectors = [Vector3(*v) for v in flattenTupleList(vectors)]
        except IndexError:
            raise IndexError("%s is not a valid input for vectors.\n" % str(vectors) +
                             "Do you need to wrap the vectors in a list?")
        except TypeError:
            raise TypeError("Can't create a vector from %s.\n" % str(vectors))

        self.__vectors = []
        # map vectors to points
        for ptCount in xrange(len(self.points)):
            try:
                self.__vectors.append(__vectors[ptCount])
            except IndexError:
                # match longest list. append the last item on the list
                try:
                    self.__vectors.append(__vectors[-1])
                except IndexError:
                    self.__vectors.append(Vector3(0, 0, 1))
            finally:
                # create an analysis point for this pionts
                self.__analysisPoints.append(
                    AnalysisPoint(self.points[ptCount], self.vectors[ptCount])
                )

    @property
    def analysisPoints(self):
        """Return a list of analysis points."""
        return self.__analysisPoints

    def toRadString(self):
        """Return analysis points group as a Radiance string."""
        __aps = []
        for ap in self.analysisPoints:
            __aps.append(ap.toRadString())

        return "\n".join(__aps)

    def __repr__(self):
        """Return analysis points and directions."""
        return self.toRadString()
