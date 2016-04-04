from honeybee.radiance.parameters.gendaymtx import GendaymtxParameters
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
dmtxpar = GendaymtxParameters()

# ask only for direct sun
dmtxpar.onlyDirect = True

# dmtx = Gendaymtx(weaFile="C:\ladybug\IZMIR_TUR\IZMIR_TUR.wea",
#                  gendaymtxParameters=dmtxpar)

dmtx = Gendaymtx(weaFile="C:\ladybug\IZMIR_TUR\IZMIR_TUR.wea")
# dmtx.gendaymtxParameters.verboseReport = False
dmtx.execute()
