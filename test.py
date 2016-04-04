from honeybee.radiance.sky.certainIlluminance import SkyWithCertainIlluminanceLevel as radSky
from honeybee.radiance.recipe.gridbased import HBGridBasedAnalysisRecipe

sky = radSky(1000)
rp = HBGridBasedAnalysisRecipe(sky, pointGroups=[0, 0, 0])

print rp.radianceParameters
rp.writeToFile("c:\\ladybug", "test3")
rp.run(debug=False)
print
print rp.results(flattenResults=True)
