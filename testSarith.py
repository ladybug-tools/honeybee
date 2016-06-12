# coding=utf-8
import os
from honeybee.radiance.recipe.annual import HBAnnualAnalysisRecipe

epwFile = r"C:\Users\Administrator\Documents\GitHub\honeybee\tests\room\test.epw"
pts = [[(0, 0, 0), (0, 0, 1)]]
analysis = HBAnnualAnalysisRecipe(epwFile, pts)
analysis.writeToFile(r"c:\ladybug", "annual")
analysis.run()
print analysis.results()
