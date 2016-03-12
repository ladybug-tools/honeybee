"""Radiance Analysis Recipes."""

from gridbased import HBGridBasedAnalysisRecipe


class HBAnnualAnalysisRecipe(HBGridBasedAnalysisRecipe):
    """Annual Daylight Recipe."""

    def __init__(self):
        """Create annual daylight recipe."""
        raise NotImplementedError()
