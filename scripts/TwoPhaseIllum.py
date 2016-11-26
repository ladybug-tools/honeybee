# coding=utf-8
"""
Date: 08/22/2016
By: Sarith Subramaniam (@sariths)
Subject: Gridpoint based implementation of 2 Phase method using native Radiance
         binary files only.
Purpose: Prototype for showing illuminance calculations using 2 Phase.
Keywords: Radiance, Grid-Based, Illuminance
"""

from honeybee.radiance.parameters.rfluxmtx import RfluxmtxParameters
from honeybee.radiance.command.rfluxmtx import Rfluxmtx
from honeybee.radiance.command.epw2wea import Epw2wea
from honeybee.radiance.command.gendaymtx import Gendaymtx,GendaymtxParameters
from honeybee.radiance.command.rmtxop import Rmtxop, RmtxopParameters
from honeybee.radiance.command.genskyvec import Genskyvec
from honeybee.radiance.command.gensky import Gensky,GenskyParameters

import os

os.chdir(r'../tests/room')
# Step1: Create annual daylight vectors through epw2wea and gendaymtx.

if not os.path.exists('temp'):
    os.mkdir('temp')

def run2Phase(calculationType='annual'):
    if calculationType == 'annual':
        weaFile = Epw2wea(epwFile='test.epw', outputWeaFile=r'temp/test.wea')
        weaFile.execute()
        gendayParam = GendaymtxParameters()
        gendayParam.skyDensity = 4

        genday = Gendaymtx(weaFile=r'temp/test.wea', outputName=r'temp/day.smx')
        genday.gendaymtxParameters = gendayParam
        # genday.execute()
        skyVector = r'temp/day.smx'
    else:
        gensk = Gensky()
        gensk.monthDayHour = (11, 11, 11)
        gensk.outputFile = 'temp/sky.rad'
        gensk.execute()

        genskv = Genskyvec()
        genskv.inputSkyFile = r'temp/sky.rad'
        genskv.outputFile = r'temp/sky.vec'
        genskv.skySubdivision = 4
        genskv.execute()
        skyVector = r'temp/sky.vec'

    #
    # Step2: Generate daylight coefficients using rfluxmtx.
    rfluxPara = RfluxmtxParameters()
    rfluxPara.irradianceCalc = False
    rfluxPara.ambientAccuracy = 0.1
    rfluxPara.ambientDivisions = 10
    rfluxPara.ambientBounces = 1
    rfluxPara.limitWeight = 0.1
    rfluxPara.quality = 0
    rflux = Rfluxmtx()
    rflux.sender = '-'
    skyFile = rflux.defaultSkyGround(r'temp/rfluxSky.rad',skyType='r4')
    rflux.receiverFile = skyFile
    rflux.rfluxmtxParameters = rfluxPara
    rflux.radFiles = [r"room.mat",
                      r"room.rad"]

    rflux.pointsFile = r"indoor_points.pts"
    rflux.outputMatrix = r"temp/dayCoeff.dc"
    rflux.execute()


    mtx1 = Rmtxop(matrixFiles=(os.path.abspath(r'temp/dayCoeff.dc'),
                               os.path.abspath(skyVector)),
                  outputFile=r'temp/illuminance.tmp')

    mtx1.execute()


    mtx2Param = RmtxopParameters()
    mtx2Param.outputFormat = 'a'
    mtx2Param.combineValues = (47.4, 119.9, 11.6)
    # mtx2Param.transposeMatrix = True
    mtx2 = Rmtxop(matrixFiles=[r'temp/illuminance.tmp'], outputFile=r'temp/illuminance.ill')
    mtx2.rmtxopParameters = mtx2Param
    mtx2.execute()

    with open(r'temp/illuminance.ill') as illFile:
        for lines in illFile:
            try:
                print(map(float, lines.split()))
            except ValueError:
                pass

#Change the calculationType to 'annual' to run an annual calculation. Any other
# input will result in a point in type calcualtion using genskyvec.
run2Phase(calculationType='annual')