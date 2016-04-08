# coding=utf-8

from honeybee.radiance.parameters.gensky import GenSkyParameters
from honeybee.radiance.parameters.gridbased import GridBasedParameters
from honeybee.radiance.command.gensky import GenSky

from honeybee.radiance.parameters.gendaymtx import GendaymtxParameters
from honeybee.radiance.command.gendaymtx import Gendaymtx

# create and modify genskyParameters. In this case a sunny with no sun
# will be generated.
gnskyParam = GenSkyParameters()
gnskyParam.sunnySky = True

# print(gnskyParam.toRadString())

# # create the gensky Command.
gnsky = GenSky(monthDayHour=(1, 1, 11), genskyParameters=gnskyParam)

print(gnsky.toRadString())
# # run gensky
output = gnsky.execute()

print output

# Using class method
# sky2 = GenSky.fromSkyType(monthDayHour=(1, 1, 11), skyType=2)
# print sky2.toRadString()

sky3 = GenSky.createUniformSkyfromIlluminanceValue(illuminanceValue=10000)
print sky3.toRadString()
