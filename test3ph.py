# coding=utf-8
from honeybee.radiance.parameters.rfluxmtx import RfluxmtxParameters
from honeybee.radiance.command.rfluxmtx import Rfluxmtx
from honeybee.radiance.command.epw2wea import Epw2wea
from honeybee.radiance.command.gendaymtx import Gendaymtx,GendaymtxParameters
from honeybee.radiance.command.rmtxop import Rmtxop, RmtxopParameters
from honeybee.radiance.command.xform import Xform,XformParameters
from honeybee.radiance.command.getbbox import Getbbox
from honeybee.radiance.command.dctimestep import Dctimestep,DctimestepParameters
from honeybee.radiance.command.genskyvec import Genskyvec
from honeybee.radiance.command.gensky import Gensky,GenskyParameters

import os

os.chdir(r'tests\room')
def run3phase(phasesToCalculate={'v':True,'t':True,'d':True,'s':True},
              calculationType='annual',epwFile=None,tmatrixFile=None):



    if phasesToCalculate['v']:
        # Step1: Create the view matrix.
        rfluxPara = RfluxmtxParameters()
        rfluxPara.I = True
        rfluxPara.aa = 0.1
        rfluxPara.ab = 10
        rfluxPara.ad = 65536
        rfluxPara.lw = 1E-5

        #step 1.1 Invert glazing surface with xform so that it faces inwards
        xfrPara = XformParameters()
        xfrPara.invertSurfaces = True

        xfr = Xform()
        xfr.xformParameters = xfrPara
        xfr.radFile = 'glazing.rad'
        xfr.outputFile = 'glazingI.rad'
        xfr.execute()

        rflux = Rfluxmtx()
        rflux.sender = '-'

        #Klems full basis sampling and the window faces +Y
        recCtrlPar = rflux.ControlParameters(hemiType='kf',hemiUpDirection='+Z')
        rflux.receiverFile = rflux.addControlParameters('glazingI.rad',
                                                        {'Exterior_Window':recCtrlPar})
        rflux.rfluxmtxParameters = rfluxPara
        rflux.pointsFile = 'indoor_points.pts'
        rflux.outputMatrix = r'temp/vmatrix.vmx'
        rflux.radFiles = ['room.mat','room.rad','glazing.rad']
        rflux.execute()

    vMatrix = r'temp/vmatrix.vmx'



    #Step2: Assign T matrix from precalculated XML files.
    tMatrix = tmatrixFile or r'xmls/clear.xml'

    if phasesToCalculate['d']:
        #Step3: Create D matrix.
        rfluxPara = RfluxmtxParameters()
        rfluxPara.aa = 0.1
        rfluxPara.ad = 1024
        rfluxPara.ab = 2
        rfluxPara.lw = 0.0000001

        rflux2 = Rfluxmtx()
        rflux2.samplingRaysCount = 1000
        rflux2.sender = 'glazingI.rad_m'
        skyFile = rflux2.defaultSkyGround(r'temp\rfluxSky.rad',skyType='r4')
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
            weaFile = Epw2wea(epwFile=epwFile or 'test.epw', outputWeaFile=r'temp\test.wea')
            weaFile.execute()

            gendayParam = GendaymtxParameters()
            gendayParam.skyDensity = 4

            genday = Gendaymtx(weaFile=r'temp\test.wea', outputName=r'temp\day.smx')
            genday.gendaymtxParameters = gendayParam
            genday.execute()

            skyVector = r'temp/day.smx'
        else:
            genskPar = GenskyParameters()
            gensk = Gensky()
            gensk.monthDayHour = (11,11,11)
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



    #Step5: Generate results
    dct = Dctimestep()
    dct.tmatrixFile = tMatrix
    dct.vmatrixSpec = vMatrix
    dct.dmatrixFile = dMatrix
    dct.skyVectorFile = skyVector
    dct.outputFileName = r'temp/results.txt'
    dct.execute()

    return 'temp/results.txt'

phases={'v':False,'t':True,'d':False,'s':False}
tmatrices = ['xmls/clear.xml', 'xmls/diffuse50.xml', 'xmls/ExtVenetianBlind_17tilt.xml']

epwFiles = ['epws/USA_AK_Anchorage.Intl.AP.702730_TMY3.epw',
            'epws/USA_KY_London-Corbin-Magee.Field.724243_TMY3.epw',
            'epws/USA_MA_Boston-City.WSO_TMY.epw',
            'epws/USA_NC_Charlotte-Douglas.Intl.AP.723140_TMY3.epw',
            'epws/USA_OH_Cleveland-Burke.Lakefront.AP.725245_TMY3.epw',
            'epws/USA_PA_Philadelphia.Intl.AP.724080_TMY3.epw']
for matrix in tmatrices:
    resultsFile= run3phase(calculationType='single',tmatrixFile=matrix,
                           phasesToCalculate=phases,epwFile=epwFiles[1])

    with open(resultsFile) as results:
        for lines in results:
            print(lines)









