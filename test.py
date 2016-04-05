from honeybee.radiance.parameters.rcontrib import RcontribParameters
from honeybee.radiance.command.gendaymtx import Gendaymtx
import os
# sky = radSky(1000)
# rp = HBGridBasedAnalysisRecipe(sky, pointGroups=[0, 0, 0])
#
# print rp.radianceParameters
# rp.writeToFile("c:\\ladybug", "test3")
# rp.run(debug=False)
# print
# print rp.results(flattenResults=True)


# generate sky matrix with default values
rcp = RcontribParameters()

# ask only for direct sun
print rcp.toRadString()

rcp.modFile = "c:/ladybug/suns.txt"
print rcp.toRadString()

rcp.I = True
rcp.ab = 0
rcp.ad = 10000
print rcp.toRadString()

rcp.quality = 1
print rcp.toRadString()

# dmtx = Gendaymtx(weaFile="C:\ladybug\IZMIR_TUR\IZMIR_TUR.wea",
#                  gendaymtxParameters=dmtxpar)

# dmtx = Gendaymtx(weaFile="C:\ladybug\IZMIR_TUR\IZMIR_TUR.wea")
# dmtx.gendaymtxParameters.verboseReport = False
# dmtx.execute()
