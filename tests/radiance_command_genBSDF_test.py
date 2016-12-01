from honeybee.radiance.parameters.genBsdf import GenbsdfParameters
from honeybee.radiance.command.genBSDF import GenBSDF,GridBasedParameters
from honeybee.radiance.command.rmtxop import Rmtxop,RmtxopParameters


y = GenbsdfParameters()
y.numProcessors=10
y.geomUnitIncl='meter'


z = GenBSDF()
z.gridBasedParameters = GridBasedParameters()
z.gridBasedParameters.ambientBounces = 1
z.genBsdfParameters = y
z.inputGeometry = ['room/room.mat','room/glazing.rad']
z.outputFile = 'room/test.xml'
z.normalOrientation='-Y'
z.execute()

rmtPara = RmtxopParameters()
rmtPara.outputFormat = 'c'

rmt = Rmtxop()
rmt.rmtxopParameters = rmtPara
rmt.matrixFiles = ['room/test.xml']
rmt.outputFile = 'room/testhdr.tmp'
rmt.execute()

import os

os.system('pfilt -x 800 -y 800 %s > room/testhdr.hdr'%rmt.outputFile)
os.system('ra_bmp %s > room/testhdr.bmp'%'room/testhdr.hdr')

os.startfile(os.path.abspath('room/testhdr.bmp'))

