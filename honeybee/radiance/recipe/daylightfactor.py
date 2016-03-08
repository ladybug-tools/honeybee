"""Radiance Analysis Recipes."""

from gridbased import HBGridBasedAnalysisRecipe


class HBDaylightFactorRecipe(HBGridBasedAnalysisRecipe):
    """Daylight Factor Recipe."""

    def __init__(self):
        """Create daylight factor recipe."""
        raise NotImplementedError()
