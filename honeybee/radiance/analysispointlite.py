"""A light version of test points."""
from __future__ import division
from ..vectormath.euclid import Point3, Vector3


class AnalysisPointLite(object):
    """A radiance analysis point.

    Attributes:
        location: Location of analysis points as (x, y, z).
        direction: Direction of analysis point as (x, y, z).

    This class is developed to enable honeybee for running daylight control
    studies with dynamic shadings without going back to several files.

    Each AnalysisPoint can load annual total and direct results for every state of
    each source assigned to it. As a result once can end up with a lot of data for
    a single point (8760 * sources * states for each source). The data are sorted as
    integers and in different lists for each source. There are several methods to
    set or get the data but if you're interested in more details read the comments
    under __init__ to know how the data is stored.

    In this class:
     - Id stands for 'the id of a blind state'. Each state has a name and an ID will
       be assigned to it based on the order of loading.
     - coupledValue stands for a tuple of  (total, direct) values. If one the values is
       not available it will be set to None.

    """

    __slots__ = ('_loc', '_dir')

    def __init__(self, location, direction):
        """Create an analysis point."""
        self.location = location
        self.direction = direction

    @classmethod
    def from_json(cls, ap_json):
        """Create an analysis point from json object.
            {"location": [x, y, z], "direction": [x, y, z]}
        """
        return cls(ap_json['location'], ap_json['direction'])

    @classmethod
    def from_raw_values(cls, x, y, z, x1, y1, z1):
        """Create an analysis point from 6 values.

        x, y, z are the location of the point and x1, y1 and z1 is the direction.
        """
        return cls((x, y, z), (x1, y1, z1))

    @property
    def location(self):
        """Location of analysis points as Point3."""
        return self._loc

    @location.setter
    def location(self, location):
        try:
            self._loc = Point3(*(float(l) for l in location))
        except TypeError:
            try:
                # Dynamo Points!
                self._loc = Point3(location.X, location.Y, location.Z)
            except Exception as e:
                raise TypeError(
                    'Failed to convert {} to location.\n'
                    'location should be a list or a tuple with 3 values.\n{}'
                    .format(location, e))

    @property
    def direction(self):
        """Direction of analysis points as Point3."""
        return self._dir

    @direction.setter
    def direction(self, direction):
        try:
            self._dir = Vector3(*(float(d) for d in direction))
        except TypeError:
            try:
                # Dynamo Points!
                self._dir = Vector3(direction.X, direction.Y, direction.Z)
            except Exception as e:
                raise TypeError(
                    'Failed to convert {} to direction.\n'
                    'location should be a list or a tuple with 3 values.\n{}'
                    .format(direction, e))

    def duplicate(self):
        """Duplicate the analysis point."""
        return self

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def to_rad_string(self):
        """Return Radiance string for a test point."""
        return "%s %s" % (self.location, self.direction)

    def to_json(self):
        """Create an analysis point from json object.
            {"location": [x, y, z], "direction": [x, y, z]}
        """
        return {"location": list(self.location),
                "direction": list(self.direction)}

    def __repr__(self):
        """Print an analysis point."""
        return 'AnalysisPoint::(%s)::(%s)' % (self.location, self.direction)
