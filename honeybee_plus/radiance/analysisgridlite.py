"""Honeybee PointGroup and TestPointGroup."""
from __future__ import division
from ..utilcol import random_name
from ..futil import write_to_file_by_name
from .analysispointlite import AnalysisPointLite as AnalysisPoint

import os
try:
    from itertools import izip as zip
except:
    # python 3
    pass

class AnalysisGridLite(object):
    """A grid of analysis points.

    Attributes:
        analysis_points: A collection of analysis points.
    """

    __slots__ = ('_analysis_points', '_name', '_status', '_result_files')

    def __init__(self, analysis_points, name=None):
        """Initialize a AnalysisPointGroup.

        analysis_points: A collection of AnalysisPoints.
        name: A unique name for this AnalysisGridLite.
        window_groups: A collection of window_groups which contribute to this grid.
            This input is only meaningful in studies such as daylight coefficient
            and multi-phase studies that the contribution of each source will be
            calculated separately (default: None).
        """
        self.name = name

        for ap in analysis_points:
            assert hasattr(ap, '_dir'), \
                '{} is not an AnalysisPoint.'.format(ap)

        self._analysis_points = analysis_points
        self._status = 0  # newly created

    @classmethod
    def from_json(cls, ag_json):
        """Create an analysis grid from json objects."""
        analysis_points = tuple(AnalysisPoint.from_json(pt)
                                for pt in ag_json["analysis_points"])
        return cls(analysis_points=analysis_points, name=ag_json["name"])

    @classmethod
    def from_points_and_vectors(cls, points, vectors, name=None):
        """Create an analysis grid from points and vectors.

        Args:
            points: A flatten list of (x, y ,z) points.
            vectors: An list of (x, y, z) for direction of test points.
        """
        aps = tuple(AnalysisPoint(pt, v) for pt, v in zip(points, vectors))
        return cls(aps, name)

    @classmethod
    def from_file(cls, file_path, start_line=None, end_line=None):
        """Create an analysis grid from a pts file.

        Args:
            file_path: Full path to points file
            start_line: Start line (default: 0)
            end_line: End line as an integer (default: last line in file)
        """
        start_line = int(start_line) if start_line else 0
        try:
            end_line = int(end_line)
        except TypeError:
            end_line = float('+inf')

        line_count = end_line - start_line + 1
        assert os.path.isfile(file_path), IOError("Can't find {}.".format(file_path))
        ap = AnalysisPoint  # load analysis point locally for better performance
        points = []
        with open(file_path, 'rb') as inf:
            for i in range(start_line):
                next(inf)
            for count, l in enumerate(inf):
                if not count < line_count:
                    break
                points.append(ap.from_raw_values(*l.split()))

        return cls(points)

    @property
    def isAnalysisGridLite(self):
        """Return True for AnalysisGridLite."""
        return True

    @property
    def isAnalysisGrid(self):
        """Return True for AnalysisGridLite."""
        return True

    @property
    def name(self):
        """AnalysisGridLite name."""
        return self._name

    @name.setter
    def name(self, n):
        self._name = n or random_name()

    @property
    def points(self):
        """A generator of points as x, y, z."""
        return (ap.location for ap in self._analysis_points)

    @property
    def vectors(self):
        """Get generator of vectors as x, y , z."""
        return (ap.direction for ap in self._analysis_points)

    @property
    def status(self):
        """AnalysisGridLite status.
            -1 - removed
            0 - created
            1 - modified
            2 - unchanged
        """
        return self._status

    @status.setter
    def status(self, n):
        self._status = n

    @property
    def analysis_points(self):
        """Return a list of analysis points."""
        return self._analysis_points

    def duplicate(self):
        """Duplicate AnalysisGridLite."""
        return self

    def to_rad_string(self):
        """Return analysis points group as a Radiance string."""
        return "\n".join((ap.to_rad_string() for ap in self._analysis_points))

    def write(self, folder, filename=None, mkdir=False):
        """write analysis grid to file."""
        name = filename or self.name + '.pts'
        return write_to_file_by_name(folder, name, self.to_rad_string() + '\n', mkdir)

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def to_json(self):
        """Create json object from AnalysisGridLite."""
        analysis_points = [ap.to_json() for ap in self.analysis_points]
        return {
            "name": self._name,
            "analysis_points": analysis_points
        }

    def __len__(self):
        """Number of points in this group."""
        return len(self._analysis_points)

    def __getitem__(self, index):
        """Get value for an index."""
        return self._analysis_points[index]

    def __iter__(self):
        """Iterate points."""
        return iter(self._analysis_points)

    def __str__(self):
        """String repr."""
        return self.to_rad_string()

    def __repr__(self):
        """Return analysis points and directions."""
        return 'AnalysisGridLite::{}::#{}'.format(
            self._name, len(self._analysis_points)
        )
