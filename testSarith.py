# coding=utf-8

from honeybee.radiance.parameters.gensky import GenSkyParameters
from honeybee.radiance.command.gensky import GenSky

from honeybee.radiance.parameters.gendaymtx import GendaymtxParameters
from honeybee.radiance.command.gendaymtx import Gendaymtx

# create and modify genskyParameters. In this case a sunny with no sun
# will be generated.
gnskyParam = GenSkyParameters()
print(gnskyParam.toRadString())
gnskyParam.sunnySkyNoSun = True

print(gnskyParam.toRadString())

assert 0
# create the gensky Command.
gnsky = GenSky(monthDayHour=(1,1,11),genskyParameters=gnskyParam,
outputName = r'd:\sky.rad' )

print(gnsky.toRadString())
# run gensky
gnsky.execute()

