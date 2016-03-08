"""Radiance Analysis workflows."""


# TODO: (@sariths) Add electrical lighting as an input.
class AnalysisBase(object):
    """Base analysis class for Radiance analysis."""

    def __init__(self, HBObjects, analysisRecipe, otherRADFiles=None):
        """Create an analysis by HBSky and HBObjects.

        Args:
            HBSky: A honeybee.radiance.sky
            analysisRecipe: A honeybee.radiance.analysisRecipe
            HBObjects: A list of Honeybee surfaces or zones
            otherRADFiles: An ordered list of additional radiance file to be
                added to the analysis.
        """
        pass

    @property
    def isRunning(self):
        """Return is analysis is still running."""
        pass

    @property
    def isOver(self):
        """Return if analysis is done."""
        pass

    @property
    def progress(self):
        """Return progress value between 0-100."""
        pass

    def write(self):
        """Write analysis files."""
        pass

    def run(self, minimize=False, wait=True):
        """Run analysis."""
        pass

    def results(self):
        """Get analysis results."""
        pass

    def __repr__(self):
        """Represent Analysis class."""
        return "honeybee.Analysis.%s" % self.__class__.__name__
