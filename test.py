from honeybee.radiance.recipe.sunlighthours import HBSunlightHoursAnalysisRecipe
from honeybee.ladybug.core import AnalysisPeriod
from honeybee.ladybug.epw import EPW

# print os.environ
testPts = [(0, 0, 0)]
testVec = [(-1, 0, 0)]
sunVectors = ((-0.810513, 0.579652, -0.084093), (-0.67166, 0.702357, -0.235729),
              (-0.487065, 0.798284, -0.354275), (-0.269301, 0.8609, -0.431657),
              (-0.033196, 0.885943, -0.462605), (0.20517, 0.871705, -0.445013),
              (0.429563, 0.819156, -0.380077), (0.624703, 0.731875, -0.272221),
              (0.777301, 0.615806, -0.128788))

# slh = HBSunlightHoursAnalysisRecipe(sunVectors, testPts, testVec)
# slh.writeToFile("c:/ladybug", projectName="1")
# if slh.run():
#     print slh.results()[0] == 4

epwfile = r"C:\EnergyPlusV8-3-0\WeatherData\USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
location = EPW(epwfile).location
ap = AnalysisPeriod(stMonth=1, endMonth=3)

slh = HBSunlightHoursAnalysisRecipe.fromLocationAndAnalysisPeriod(
    location, ap, testPts, testVec)

slh.writeToFile("c:/ladybug", projectName="2")
if slh.run():
    print len(slh.sunVectors), slh.results()
