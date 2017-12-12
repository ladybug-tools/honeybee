"""Honeybee generic grid base analysis baseclass.

This class is base class for common gridbased analysis recipes as well as
sunlighthours recipe and annual analysis recipe.
"""

from abc import ABCMeta, abstractmethod
from ..analysisgrid import AnalysisGrid
from ...futil import write_to_file
from ...utilcol import random_name
from ._recipebase import AnalysisRecipe

from ladybug.legendparameters import LegendParameters

import os


class GenericGridBased(AnalysisRecipe):
    """Honeybee generic grid base analysis base class.

    This class is base class for common gridbased analysis recipes as well as
    sunlighthours recipe and annual analysis recipe.

    Attributes:
        analysis_grids: A collection of honeybee AnalysisGrid. Use
            from_points_and_vectors classmethod to create the recipe by points and
            vectors.
        hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
        sub_folder: Analysis subfolder for this recipe. (Default: "gridbased")
    """

    __metaclass__ = ABCMeta

    def __init__(self, analysis_grids, hb_objects=None, sub_folder="gridbased"):
        """Create grid-based recipe."""
        # keep track of original points for re-structuring them later on
        AnalysisRecipe.__init__(self, hb_objects=hb_objects, sub_folder=sub_folder)
        self.analysis_grids = analysis_grids

    @classmethod
    def from_points_and_vectors(cls, point_groups, vector_groups=None, hb_objects=None,
                                sub_folder="gridbased"):
        """Create the recipe from analysisGrid.

        Args:
            point_groups: A list of (x, y, z) test points or lists of list of (x, y, z)
                test points. Each list of test points will be converted to a
                    TestPointGroup.
                If testPts is a single flattened list only one TestPointGroup will be
                    created.
            vector_groups: An optional list of (x, y, z) vectors. Each vector represents
                direction of corresponding point in testPts. If the vector is not
                provided (0, 0, 1) will be assigned.
            hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
            sub_folder: Analysis subfolder for this recipe. (Default: "gridbased").
        """
        analysis_grids = cls.analysis_grids_from_points_and_vectors(
            point_groups, vector_groups)
        return cls(analysis_grids, hb_objects, sub_folder)

    @property
    def analysis_grids(self):
        """Return analysis grids."""
        return self._analysis_grids

    @analysis_grids.setter
    def analysis_grids(self, ags):
        """Set analysis grids."""
        self._analysis_grids = tuple(ag.duplicate() for ag in ags)

        for ag in self._analysis_grids:
            assert hasattr(ag, 'isAnalysisGrid'), \
                'Expected an AnalysisGrid not {}'.format(type(ag))

    @property
    def points(self):
        """Return nested list of points."""
        return tuple(ap.points for ap in self.analysis_grids)

    @property
    def vectors(self):
        """Nested list of vectors."""
        return tuple(ap.vectors for ap in self.analysis_grids)

    @property
    def analysis_grid_count(self):
        """Number of point groups."""
        return len(self.analysis_grids)

    @property
    def total_point_count(self):
        """Number of total points."""
        return sum(len(tuple(pts)) for pts in self.points)

    @property
    def legend_parameters(self):
        """Legend parameters for grid based analysis."""
        return LegendParameters([0, 3000])

    @staticmethod
    def analysis_grids_from_points_and_vectors(point_groups, vector_groups=None):
        """Create analysisGrid classes from points and vectors.

        Args:
            point_groups: A list of (x, y, z) test points or lists of list of (x, y, z)
                test points. Each list of test points will be converted to a
                    TestPointGroup.
                If testPts is a single flattened list only one TestPointGroup will be
                    created.
            vector_groups: An optional list of (x, y, z) vectors. Each vector represents
                direction of corresponding point in testPts. If the vector is not
                provided (0, 0, 1) will be assigned.
        """
        vector_groups = vector_groups or ((),)

        vector_groups = tuple(vector_groups[i] if i < len(vector_groups)
                              else vector_groups[-1] for i in range(len(point_groups)))

        # print(zip(point_groups, vector_groups))
        analysis_grids = (AnalysisGrid.from_points_and_vectors(pts, vectors)
                          for pts, vectors in zip(point_groups, vector_groups))

        return analysis_grids

    def write_analysis_grids(self, target_dir, file_name=None, merge=True, mkdir=False):
        """Write point groups to file.

        Args:
            target_dir: Path to project directory (e.g. c:/ladybug)
            file_name: File name as string. Points will be saved as
                file_name.pts
            merge: Merge all the grids into a single file. If the input is
                False each file will be named based on the grid name (default: True).
        Returns:
            Path to file in case of success.

        Exceptions:
            ValueError if target_dir doesn't exist and mkdir is False.
        """
        if merge:
            file_name = file_name or random_name()
            assert isinstance(file_name, str), 'file_name should be a string.'
            file_name = file_name if file_name.lower().endswith('.pts') \
                else file_name + '.pts'

            grids = '\n'.join((ag.to_rad_string() for ag in self.analysis_grids)) + '\n'
            return write_to_file(os.path.join(target_dir, file_name), grids, mkdir)
        else:
            return tuple(
                write_to_file(os.path.join(target_dir, ag.name + '.pts'),
                              ag.to_rad_string() + '\n',
                              mkdir)
                for ag in self.analysis_grids
            )

    @abstractmethod
    def results(self):
        """Return results for this analysis."""
        raise NotImplementedError()

    def ToString(self):
        """Overwriet .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represent grid based recipe."""
        return "%s\n#AnalysisGrids: %d #Points: %d" % \
            (self.__class__.__name__,
             self.analysis_grid_count,
             self.total_point_count)
