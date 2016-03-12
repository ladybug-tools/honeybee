"""Radiance Analysis Recipes."""

from recipeBase import HBDaylightAnalysisRecipe


class HBImageBasedAnalysisRecipe(HBDaylightAnalysisRecipe):
    """Image-based recipe."""

    def __init__(self):
        """Create an Image-based recipe."""
        raise NotImplementedError()
