"""Honeybee generic image based analysis baseclass.

This class is base class for common imagebased analysis recipes.
"""

from abc import ABCMeta, abstractmethod
from ...futil import write_to_file
from ._recipebase import AnalysisRecipe

import os


class GenericImageBased(AnalysisRecipe):
    """Honeybee generic grid base analysis base class.

    This class is base class for common gridbased analysis recipes as well as
    sunlighthours recipe and annual analysis recipe.

    Attributes:
        views: A collection of honeybee Views.
        hb_objects: An optional list of Honeybee surfaces or zones (Default: None).
        sub_folder: Analysis subfolder for this recipe. (Default: "gridbased")
    """

    __metaclass__ = ABCMeta

    def __init__(self, views, hb_objects=None, sub_folder="imagebased"):
        """Create image-based recipe."""
        # keep track of original points for re-structuring them later on
        AnalysisRecipe.__init__(self, hb_objects=hb_objects, sub_folder=sub_folder)
        self.views = views

    @property
    def views(self):
        """Return views."""
        return self.__views

    @views.setter
    def views(self, v):
        """Set views."""
        self.__views = v

        for v in self.__views:
            assert hasattr(v, 'isView'), \
                '{} is not a View.'.format(v)

    @property
    def view_count(self):
        """Number of point groups."""
        return len(self.views)

    def write_views(self, target_dir, mkdir=False):
        """Write point groups to file.

        Args:
            target_dir: Path to project directory (e.g. c:/ladybug)

        Returns:
            Path to file in case of success.

        Exceptions:
            ValueError if target_dir doesn't exist and mkdir is False.
        """

        return tuple(write_to_file(os.path.join(target_dir, v.name + '.vf'),
                                   'rvu ' + v.to_rad_string() + '\n',
                                   mkdir)
                     for v in self.views)

    @abstractmethod
    def results(self):
        """Return results for this analysis."""
        pass

    def ToString(self):
        """Overwriet .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represent grid based recipe."""
        return "%s\n#Views: %d" % (self.__class__.__name__, self.view_count)
