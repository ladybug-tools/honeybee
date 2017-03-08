# coding=utf-8
"""
Date: 08/22/2016
By: Sarith Subramaniam (sariths)
Subject: Gridpoint based implementation of 3 Phase method using native Radiance
         binary files only.
Purpose: Prototype for showing illuminance calculations using 3 Phase.
Keywords: Radiance, Grid-Based, Illuminance
"""

import os
import sys

if 'honeybee' not in sys.modules:
    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from honeybee.radiance.parameters.rfluxmtx import RfluxmtxParameters
from honeybee.radiance.command.rfluxmtx import Rfluxmtx
from honeybee.radiance.command.epw2wea import Epw2wea
from honeybee.radiance.command.gendaymtx import Gendaymtx, GendaymtxParameters
from honeybee.radiance.command.xform import Xform, XformParameters
from honeybee.radiance.command.dctimestep import Dctimestep
from honeybee.radiance.command.genskyvec import Genskyvec
from honeybee.radiance.command.gensky import Gensky, GenskyParameters
from honeybee.radiance.command.pcomb import PcombImage, PcombParameters, Pcomb
from honeybee.radiance.command.rmtxop import Rmtxop,RmtxopParameters

os.chdir(r'../tests/room')

if not os.path.exists('temp'):
    os.mkdir('temp')


def run3phase(phasesToCalculate={'v': True, 't': True, 'd': True, 's': True},
              calculationType='annual', epwFile=None, tmatrixFile=None):


    if phasesToCalculate['v']:
        # Step1: Create the view matrix.
        rfluxPara = RfluxmtxParameters()
        rfluxPara.irradianceCalc = True
        rfluxPara.ambientAccuracy = 0.1
        rfluxPara.ambientBounces = 10
        rfluxPara.ambientDivisions = 65536
        rfluxPara.limitWeight = 1E-5

        # step 1.1 Invert glazing surface with xform so that it faces inwards
        xfrPara = XformParameters()
        xfrPara.invertSurfaces = True

        xfr = Xform()
        xfr.xformParameters = xfrPara
        xfr.radFile = 'glazing.rad'
        xfr.outputFile = 'glazingI.rad'
        xfr.execute()

        rflux = Rfluxmtx()
        rflux.sender = '-'

        # This needs to be automated based on the normal of each window.
        # Klems full basis sampling and the window faces +Y
        recCtrlPar = rflux.ControlParameters(hemiType='kf', hemiUpDirection='+Z')
        rflux.receiverFile = rflux.addControlParameters('glazingI.rad',
                                                        {'Exterior_Window': recCtrlPar})

        rflux.rfluxmtxParameters = rfluxPara
        rflux.pointsFile = 'indoor_points.pts'
        rflux.outputMatrix = r'temp/vmatrix.vmx'
        rflux.radFiles = ['room.mat', 'room.rad']
        rflux.execute()

    vMatrix = r'temp/vmatrix.vmx'

    # Step2: Assign T matrix from precalculated XML files.
    tMatrix = tmatrixFile or r'xmls/clear.xml'

    if phasesToCalculate['d']:
        # Step3: Create D matrix.
        rfluxPara = RfluxmtxParameters()
        rfluxPara.ambientAccuracy = 0.1
        rfluxPara.ambientDivisions = 1024
        rfluxPara.ambientBounces = 2
        rfluxPara.limitWeight = 0.0000001

        rflux2 = Rfluxmtx()
        rflux2.samplingRaysCount = 1000
        rflux2.sender = 'glazingI_m.rad'
        skyFile = rflux2.defaultSkyGround(r'temp/rfluxSky.rad', skyType='r1')
        rflux2.receiverFile = skyFile
        rflux2.rfluxmtxParameters = rfluxPara
        rflux2.radFiles = [r"room.mat",
                          r"room.rad"]
        rflux2.outputMatrix = r"temp/dmatrix.dmx"
        rflux2.execute()
    dMatrix = r"temp/dmatrix.dmx"

    # Step4a: Create the sky vector.

    # Step4a.1: Create a sky defintion
    # Step s: Creating the sky matrix
    if phasesToCalculate['s']:
        if calculationType == 'annual':
            weaFile = Epw2wea(epwFile=epwFile or 'test.epw', outputWeaFile=r'temp/test.wea')
            weaFile.execute()

            gendayParam = GendaymtxParameters()
            gendayParam.skyDensity = 1

            genday = Gendaymtx(weaFile=r'temp/test.wea', outputName=r'temp/day.smx')
            genday.gendaymtxParameters = gendayParam
            genday.execute()

            skyVector = r'temp/day.smx'
        else:
            gensk = Gensky()
            gensk.monthDayHour = (11, 11, 11)
            gensk.outputFile = 'temp/sky.rad'
            # gensk.execute()

            genskv = Genskyvec()
            genskv.inputSkyFile = r'temp/sky.rad'
            genskv.outputFile = r'temp/sky.vec'
            genskv.skySubdivision = 1
            genskv.execute()
            skyVector = r'temp/sky.vec'
    else:
        skyVector = r'temp/sky.vec'

    # Step5: Generate results
    dct = Dctimestep()
    dct.tmatrixFile = tMatrix
    dct.vmatrixSpec = vMatrix
    dct.dmatrixFile = dMatrix
    dct.skyVectorFile = skyVector
    dct.outputFileName = r'temp/results3p.tmp'
    dct.execute()




    mtx2Param = RmtxopParameters()
    mtx2Param.outputFormat = 'a'
    mtx2Param.combineValues = (47.4, 119.9, 11.6)
    mtx2Param.transposeMatrix = True
    mtx2 = Rmtxop(matrixFiles=[r'temp/results3p.tmp'], outputFile=r'temp/illuminance3p.ill')
    mtx2.rmtxopParameters = mtx2Param
    mtx2.execute()

    return  'temp/illuminance3p.ill'
phases = {'v': True, 't': True, 'd': True, 's': True}
tmatrices = ('xmls/clear.xml', 'xmls/diffuse50.xml',
             'xmls/ExtVenetianBlind_17tilt.xml')

epwFiles = ['epws/USA_AK_Anchorage.Intl.AP.702730_TMY3.epw',
            'epws/USA_KY_London-Corbin-Magee.Field.724243_TMY3.epw',
            'epws/USA_MA_Boston-City.WSO_TMY.epw',
            'epws/USA_NC_Charlotte-Douglas.Intl.AP.723140_TMY3.epw',
            'epws/USA_OH_Cleveland-Burke.Lakefront.AP.725245_TMY3.epw',
            'epws/philly.epw']

for matrix in tmatrices[:1]:
    resultsFile = run3phase(calculationType='annual', tmatrixFile=matrix,
                            phasesToCalculate=phases, epwFile=epwFiles[1])

    with open(resultsFile) as results:
        for lines in results:
            try:
                lineVal = [round(val,2)for val in map(float,lines.split())]
                print(" ".join(map(str,lineVal)))
            except ValueError:
                print(lines.strip())
    assert 0