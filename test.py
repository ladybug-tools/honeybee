# coding=utf-8
from honeybee.radiance.parameters.rfluxmtx import RfluxmtxParameters
from honeybee.radiance.command.rfluxmtx import Rfluxmtx
from honeybee.radiance.command.epw2wea import Epw2wea
from honeybee.radiance.command.gendaymtx import Gendaymtx
from honeybee.radiance.command.rmtxop import Rmtxop

import os

os.chdir(r'tests\room')

#Step1: Create annual daylight vectors through epw2wea and gendaymtx.
weaFile = Epw2wea(epwFile='test.epw')
weaFile.execute()

genday = Gendaymtx(weaFile='test.wea',outputName='day.smx')
genday.execute()

#Step2: Generate daylight coefficients using rfluxmtx.
rfluxPara = RfluxmtxParameters()
rfluxPara.aa = 0.1
rfluxPara.ad= 5

rflux = Rfluxmtx()
rflux.sender = '-'
skyFile = rflux.defaultSkyGround('rfluxSky.rad')
rflux.receiverFile = skyFile
rflux.rfluxmtxParameters = rfluxPara
rflux.radFiles = [r"room.mat",
                  r"room.rad"]

rflux.pointsFile = r"indoor_points.pts"
rflux.outputMatrix = r"dayCoeff.dc"
print(rflux.toRadString())
rflux.execute()


mtx1 = Rmtxop(matrixFiles=(os.path.abspath(r'day.smx'),os.path.abspath(r'dayCoeff.dc')),
              outputFile=r'illuminance.tmp')
print(mtx1.toRadString())
mtx1.execute()