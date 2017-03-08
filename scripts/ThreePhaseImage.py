# coding=utf-8
"""
Date: 08/22/2016
By: Sarith Subramaniam (@sariths)
Subject: Image based implementation of the 3 Phase Method using native Radiance
            binary files only.
Purpose: Prototype for showing illuminance calculations using 3 Phase.
Keywords: Radiance, 3Phase, Image-Based, Luminance
"""

from honeybee.radiance.parameters.rfluxmtx import RfluxmtxParameters
from honeybee.radiance.command.rfluxmtx import Rfluxmtx
from honeybee.radiance.command.epw2wea import Epw2wea
from honeybee.radiance.command.gendaymtx import Gendaymtx,GendaymtxParameters
from honeybee.radiance.command.xform import Xform,XformParameters
from honeybee.radiance.command.dctimestep import Dctimestep
from honeybee.radiance.command.genskyvec import Genskyvec
from honeybee.radiance.command.gensky import Gensky,GenskyParameters
from honeybee.radiance.command.pcomb import PcombImage,PcombParameters,Pcomb
from honeybee.radiance.command.vwrays import Vwrays,VwraysParameters
import os



os.chdir(r'tests/room')

if not os.path.exists('temp'):
    os.mkdir('temp')


def run3phase(phasesToCalculate={'v':True,'t':True,'d':True,'s':True},
              calculationType='annual',epwFile=None,tmatrixFile=None,
              hdrResultsFileName=None,numProcessors=1,timeStamp=None):


    if phasesToCalculate['v']:
        # Step1: Create the view matrix.
        rfluxPara = RfluxmtxParameters()
        rfluxPara.ambientAccuracy = 0.1
        rfluxPara.ambientBounces = 10
        # using this for a quicker run
        rfluxPara.ambientBounces = 5

        rfluxPara.ambientDivisions = 65536
        # using this for a quicker run
        # rfluxPara.ad = 1000

        rfluxPara.limitWeight = 1E-5
        # rfluxPara.lw = 1E-2

        #step 1.1 Invert glazing surface with xform so that it faces inwards
        xfrPara = XformParameters()
        xfrPara.invertSurfaces = True

        xfr = Xform()
        xfr.xformParameters = xfrPara
        xfr.radFile = 'glazing.rad'
        xfr.outputFile = 'glazingI.rad'
        xfr.execute()

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
        # vwrParaSamp.samplingRaysCount = 3
        vwrParaSamp.jitter = 0.7

        vwrSamp = Vwrays()
        vwrSamp.vwraysParameters = vwrParaSamp
        vwrSamp.viewFile = 'viewSouth1.vf'
        vwrSamp.outputFile = r'temp/viewSouthRays.txt'
        vwrSamp.outputDataFormat = 'f'
        vwrSamp.execute()



        rflux = Rfluxmtx()
        rflux.sender = '-'

        #Klems full basis sampling and the window faces +Y
        recCtrlPar = rflux.ControlParameters(hemiType='kf',hemiUpDirection='+Z')
        rflux.receiverFile = rflux.addControlParameters('glazingI.rad',
                                                        {'Exterior_Window':recCtrlPar})
        rflux.outputDataFormat = 'fc'
        rflux.verbose = True
        rflux.rfluxmtxParameters = rfluxPara
        rflux.viewInfoFile = r'temp/viewSouthDimensions.txt'
        rflux.viewRaysFile = r'temp/viewSouthRays.txt'
        rflux.radFiles = ['room.mat','room.rad','glazing.rad']
        rflux.outputFilenameFormat = r'temp/%03d.hdr'
        rflux.samplingRaysCount = 9
        # rflux.samplingRaysCount = 3
        rflux.numProcessors = numProcessors
        rflux.execute()

    vMatrix = r'temp/vmatrix.vmx'



    #Step2: Assign T matrix from precalculated XML files.
    tMatrix = tmatrixFile or r'xmls/clear.xml'

    if phasesToCalculate['d']:
        #Step3: Create D matrix.
        rfluxPara = RfluxmtxParameters()
        rfluxPara.ambientAccuracy = 0.1
        rfluxPara.ambientDivisions = 1024
        rfluxPara.ambientBounces = 2
        rfluxPara.limitWeight = 0.0000001

        rflux2 = Rfluxmtx()
        rflux2.numProcessors = numProcessors
        rflux2.samplingRaysCount = 1000
        rflux2.sender = 'glazingI.rad_m'
        skyFile = rflux2.defaultSkyGround(r'temp/rfluxSky.rad', skyType='r4')
        rflux2.receiverFile = skyFile
        rflux2.rfluxmtxParameters = rfluxPara
        rflux2.radFiles = [r"room.mat",
                          r"room.rad",
                          'glazing.rad']
        rflux2.outputMatrix = r"temp/dmatrix.dmx"
        rflux2.execute()

    dMatrix = r"temp/dmatrix.dmx"


    #Step4a: Create the sky vector.

    #Step4a.1: Create a sky defintion
    # Step s: Creating the sky matrix
    if phasesToCalculate['s']:
        if calculationType == 'annual':
            weaFile = Epw2wea(epwFile=epwFile or 'test.epw', outputWeaFile=r'temp/test.wea')
            weaFile.execute()

            gendayParam = GendaymtxParameters()
            gendayParam.skyDensity = 4

            genday = Gendaymtx(weaFile=r'temp/test.wea', outputName=r'temp/day.smx')
            genday.gendaymtxParameters = gendayParam
            genday.execute()

            skyVector = r'temp/day.smx'
        else:
            genskPar = GenskyParameters()
            gensk = Gensky()
            gensk.monthDayHour = timeStamp or (11,11,11)
            gensk.outputFile = 'temp/sky.rad'
            gensk.execute()

            genskv = Genskyvec()
            genskv.inputSkyFile = r'temp/sky.rad'
            genskv.outputFile = r'temp/sky.vec'
            genskv.skySubdivision = 4
            genskv.execute()
            skyVector = r'temp/sky.vec'
    else:
        skyVector = r'temp/sky.vec'



    # Step5: Generate results
    dct = Dctimestep()
    dct.tmatrixFile = tMatrix
    dct.vmatrixSpec = r'temp/%03d.hdr'
    dct.dmatrixFile = dMatrix
    dct.skyVectorFile = skyVector
    dct.outputFileName = hdrResultsFileName or r'temp/results.hdr'
    dct.execute()

    return 'temp/results.txt'


if __name__ == '__main__':
    phases = {'v': True, 't': True, 'd': True, 's': False}
    tmatrices = ['xmls/clear.xml', 'xmls/diffuse50.xml', 'xmls/ExtVenetianBlind_17tilt.xml']

    epwFiles = ['epws/USA_AK_Anchorage.Intl.AP.702730_TMY3.epw',
                'epws/USA_KY_London-Corbin-Magee.Field.724243_TMY3.epw',
                'epws/USA_MA_Boston-City.WSO_TMY.epw',
                'epws/USA_NC_Charlotte-Douglas.Intl.AP.723140_TMY3.epw',
                'epws/USA_OH_Cleveland-Burke.Lakefront.AP.725245_TMY3.epw',
                'epws/philly.epw']

    timeStamps = [(11, 11, idx) for idx in range(8, 18)]


    for idx, timeStamp in enumerate(timeStamps):
        if idx:
            phases = {'v': False, 't': True, 'd': False, 's': True}

        resultsFile = run3phase(calculationType='single', tmatrixFile=tmatrices[0],
                               phasesToCalculate=phases, epwFile=epwFiles[1],
                               hdrResultsFileName=r'temp/results%s.hdr' % idx,
                                numProcessors=32,timeStamp=timeStamp)

        # with open(resultsFile) as results:
        #     for lines in results:
        #         print(lines)
