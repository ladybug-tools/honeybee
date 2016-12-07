"""
Date: 08/24/2016
By: Sarith Subramaniam (@sariths)
Subject: Image based implementation of the 2 Phase Method using native Radiance
            binary files only.
Purpose: Prototype for showing illuminance calculations using 2 Phase.
Keywords: Radiance, 2Phase, Image-Based, Luminance
"""

import os
import sys

if 'honeybee' not in sys.modules:
    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import honeybee.config
honeybee.config.perlExePath = r'C:\Program Files\OpenStudio 1.13.0\strawberry-perl-5.16.2.1-32bit-portable-reduced\perl\bin\perl.exe'

from honeybee.radiance.parameters.rfluxmtx import RfluxmtxParameters
from honeybee.radiance.command.rfluxmtx import Rfluxmtx
from honeybee.radiance.command.epw2wea import Epw2wea
from honeybee.radiance.command.gendaymtx import Gendaymtx,GendaymtxParameters
from honeybee.radiance.command.dctimestep import Dctimestep
from honeybee.radiance.command.genskyvec import Genskyvec
from honeybee.radiance.command.gensky import Gensky,GenskyParameters
from honeybee.radiance.command.vwrays import Vwrays,VwraysParameters


os.chdir(r'../tests/room')

def runDc(phasesToCalculate={'dc': True, 's': True}, calculationType='single',
          epwFile=None, hdrResultsFileName=None, timeStamp=None,skyDensity=1):

    if phasesToCalculate['dc']:
        # Step1: Create the view matrix.
        vwrParaDim = VwraysParameters()
        vwrParaDim.calcImageDim = True
        vwrParaDim.xResolution = 800
        vwrParaDim.yResolution = 800

        vwrDim = Vwrays()
        vwrDim.vwraysParameters = vwrParaDim
        vwrDim.viewFile = 'viewSouth1.vf'
        vwrDim.outputFile = r'temp/viewSouthDimensions.txt'
        vwrDim.execute()

        vwrParaSamp = VwraysParameters()
        vwrParaSamp.xResolution = 800
        vwrParaSamp.yResolution = 800
        vwrParaSamp.samplingRaysCount = 9
        vwrParaSamp.samplingRaysCount = 3
        vwrParaSamp.jitter = 0.7

        vwrSamp = Vwrays()
        vwrSamp.vwraysParameters = vwrParaSamp
        vwrSamp.viewFile = 'viewSouth1.vf'
        vwrSamp.outputFile = r'temp/viewSouthRays.txt'
        vwrSamp.outputDataFormat = 'f'
        vwrSamp.execute()

        rfluxPara = RfluxmtxParameters()
        rfluxPara.ambientAccuracy = 0.1
        # rfluxPara.ambientBounces = 10
        # using this for a quicker run
        rfluxPara.ambientBounces = 5

        # rfluxPara.ambientDivisions = 65536
        # using this for a quicker run
        rfluxPara.ambientDivisions = 2000

        # rfluxPara.limitWeight = 1E-5
        rfluxPara.limitWeight = 1E-2

        rflux = Rfluxmtx()
        rflux.sender = '-'
        groundFileFormat = 'temp/viewSouth%s.hdr' % (1 + 144 * (skyDensity ** 2))
        # Klems full basis sampling and the window faces +Y
        rflux.receiverFile = rflux.defaultSkyGround(r'temp/rfluxSky.rad', skyType='r1',
                                                    groundFileFormat=groundFileFormat,
                                                    skyFileFormat=r'temp/%03d.hdr')

        rflux.outputDataFormat = 'fc'
        rflux.verbose = True
        rflux.numProcessors = 8
        rflux.rfluxmtxParameters = rfluxPara
        rflux.viewInfoFile = r'temp/viewSouthDimensions.txt'
        rflux.viewRaysFile = r'temp/viewSouthRays.txt'
        rflux.radFiles = ['room.mat', 'room.rad', 'glazing.rad']
        rflux.samplingRaysCount = 9
        rflux.samplingRaysCount = 3
        rflux.execute()

    # Step4a: Create the sky vector.

    # Step4a.1: Create a sky defintion
    # Step s: Creating the sky matrix
    if phasesToCalculate['s']:
        if calculationType == 'annual':
            weaFile = Epw2wea(epwFile=epwFile or 'test.epw', outputWeaFile=r'temp/test.wea')
            weaFile.execute()

            gendayParam = GendaymtxParameters()
            gendayParam.skyDensity = skyDensity

            genday = Gendaymtx(weaFile=r'temp/test.wea', outputName=r'temp/day.smx')
            genday.gendaymtxParameters = gendayParam
            genday.execute()

            skyVector = r'temp/day.smx'
        else:
            gensk = Gensky()
            gensk.monthDayHour = timeStamp or (11, 11, 11)
            gensk.outputFile = 'temp/sky.rad'
            gensk.execute()

            genskv = Genskyvec()
            genskv.inputSkyFile = os.path.abspath(r'temp/sky.rad')
            genskv.outputFile = os.path.abspath(r'temp/sky.vec')
            genskv.skySubdivision = skyDensity
            genskv.execute()
            skyVector = r'temp/sky.vec'
    else:
        skyVector = r'temp/sky.vec'

    # Step5: Generate results
    dct = Dctimestep()
    dct.daylightCoeffSpec = r'temp/%03d.hdr'
    dct.skyVectorFile = skyVector
    dct.outputFile = r'temp/results.hdr'
    dct.execute()

    return 'temp/results.txt'

phases = {'dc': True, 's': True}
tmatrices = ['xmls/clear.xml', 'xmls/diffuse50.xml', 'xmls/ExtVenetianBlind_17tilt.xml']

epwFiles = ['epws/USA_AK_Anchorage.Intl.AP.702730_TMY3.epw',
            'epws/USA_KY_London-Corbin-Magee.Field.724243_TMY3.epw',
            'epws/USA_MA_Boston-City.WSO_TMY.epw',
            'epws/USA_NC_Charlotte-Douglas.Intl.AP.723140_TMY3.epw',
            'epws/USA_OH_Cleveland-Burke.Lakefront.AP.725245_TMY3.epw',
            'epws/philly.epw']

timeStamps = ((11, 6, 11),)  # [(11, 11, idx) for idx in range(8, 9)]
for idx, timeStamp in enumerate(timeStamps):

    resultsFile = runDc(calculationType='single',
                        phasesToCalculate=phases, epwFile=epwFiles[1],
                        hdrResultsFileName=r'temp/%shrs.hdr' % timeStamp[-1],
                        timeStamp=timeStamp)
