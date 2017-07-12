"""Honeybee generic image based analysis baseclass.

This class is base class for common imagebased analysis recipes.
"""

from abc import ABCMeta, abstractmethod
from ...futil import writeToFile
from ._recipebase import AnalysisRecipe

import os


class GenericImageBased(AnalysisRecipe):
    """Honeybee generic grid base analysis base class.

    This class is base class for common gridbased analysis recipes as well as
    sunlighthours recipe and annual analysis recipe.

    Attributes:
        views: A collection of honeybee Views.
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "gridbased")
    """

    __metaclass__ = ABCMeta

    def __init__(self, views, hbObjects=None, subFolder="imagebased"):
        """Create image-based recipe."""
        # keep track of original points for re-structuring them later on
        AnalysisRecipe.__init__(self, hbObjects=hbObjects, subFolder=subFolder)
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
    def viewCount(self):
        """Number of point groups."""
        return len(self.views)

    def writeViews(self, targetDir, mkdir=False):
        """Write point groups to file.

        Args:
            targetDir: Path to project directory (e.g. c:/ladybug)

        Returns:
            Path to file in case of success.

        Exceptions:
            ValueError if targetDir doesn't exist and mkdir is False.
        """

        return tuple(writeToFile(os.path.join(targetDir, v.name + '.vf'),
                                 'rvu ' + v.toRadString() + '\n',
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
        return "%s\n#Views: %d" % (self.__class__.__name__, self.viewCount)
