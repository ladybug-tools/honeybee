# coding=utf-8
"""
Date: 03/28/2017
By: Sarith Subramaniam (@sariths)
Subject: Improved daylight coefficient method.
Purpose: -
Keywords: Radiance, Grid-Based, Illuminance
"""

from honeybee.radiance.parameters.rfluxmtx import RfluxmtxParameters
from honeybee.radiance.command.rfluxmtx import Rfluxmtx
from honeybee.radiance.command.epw2wea import Epw2wea
from honeybee.radiance.command.gendaymtx import Gendaymtx,GendaymtxParameters
from honeybee.radiance.command.rmtxop import Rmtxop, RmtxopParameters,RmtxopMatrix
import time,warnings
import os
from sunPathIlluminance import calcDirectIlluminance
from honeybee.radiance.command.dctimestep import Dctimestep,DctimestepParameters
from itertools import izip



def improvedDCcalc(epwFile,materialFile, geometryFiles, pointsFile,folderForCalculations, outputIllFilePath,
                   reinhartPatches=1, calcDict={'skyVectors':True,'DirectDCCoeff':True,'DCCoeff':True,'DirectSun':True}):
    """
    Args:
        epwFile: Epw file path.
        materialFile: Path for a single material file.
        geometryFiles: One or more geometry files.
        pointsFile: Path for poitns file
        folderForCalculations: Folder for storing intermediate files.
        outputIllFilePath:
        reinhartPatches: Default is 1.
        calcDict: This is useful for selectively running different parts of the simulation.

    Returns:

    """
    #a sad logging hack
    statusMsg = lambda msg: "\n%s:%s\n%s\n" % (time.ctime(),msg ,"*~"*25)

    weaFilePath = os.path.join(folderForCalculations,os.path.splitext(os.path.split(epwFile)[1])[0]+'.wea')

    weaFile = Epw2wea(epwFile=epwFile, outputWeaFile=weaFilePath)
    weaFile.execute()

    #Calculate complete sky matrix.
    skyMatrix = os.path.join(folderForCalculations,'skyMatrix.mtx')
    gendayParam = GendaymtxParameters()
    gendayParam.skyDensity = reinhartPatches
    genday = Gendaymtx(weaFile=weaFilePath, outputName=skyMatrix)
    genday.gendaymtxParameters = gendayParam
    if calcDict['skyVectors']:
        print(genday.toRadString())
        genday.execute()

    #Calculate direct only matrix.
    skyMatrixDirect = os.path.join(folderForCalculations,'skyMatrixDirect.mtx')
    gendayParam = GendaymtxParameters()
    gendayParam.skyDensity = reinhartPatches
    gendayParam.onlyDirect = True
    genday = Gendaymtx(weaFile=weaFilePath, outputName=skyMatrixDirect)
    genday.gendaymtxParameters = gendayParam
    if calcDict['skyVectors']:
        print(genday.toRadString())
        genday.execute()



    skyDomeFile = os.path.join(folderForCalculations,'rfluxSky.rad')
    dcCoeffMatrix = os.path.join(folderForCalculations,'dc.mtx')
    dcCoeffMatrixDirect = os.path.join(folderForCalculations,'dcDirect.mtx')

    sceneData=[materialFile]
    #Append if single, extend if multiple
    if isinstance(geometryFiles,basestring):
        sceneData.append(geometryFiles)
    elif isinstance(geometryFiles,(tuple,list)):
        sceneData.extend(geometryFiles)

    # Step2: Generate daylight coefficients for normal sky-matrix using rfluxmtx.
    rfluxPara = RfluxmtxParameters()
    rfluxPara.irradianceCalc = True
    rfluxPara.ambientAccuracy = 0.1
    rfluxPara.ambientDivisions = 20000
    rfluxPara.ambientBounces = 5
    rfluxPara.limitWeight = 1E-7
    rfluxPara.ambientResolution = 10000


    rflux = Rfluxmtx()
    rflux.sender = '-'
    skyFile = rflux.defaultSkyGround(skyDomeFile,skyType='r%s'%reinhartPatches)
    rflux.receiverFile = skyDomeFile
    rflux.rfluxmtxParameters = rfluxPara
    rflux.radFiles = sceneData
    rflux.samplingRaysCount = 1

    rflux.pointsFile = pointsFile
    rflux.outputMatrix = dcCoeffMatrix
    if calcDict['DCCoeff']:
        rflux.execute()

    tempIll = os.path.join(folderForCalculations, 'temp.ill')
    ill = os.path.join(folderForCalculations, 'Illuminance.ill')

    dct = Dctimestep()
    dct.daylightCoeffSpec = dcCoeffMatrix
    dct.skyVectorFile = skyMatrix
    dct.outputFile = tempIll
    if calcDict['DCCoeff']:
        dct.execute()


    mtx2Param = RmtxopParameters()
    mtx2Param.outputFormat = 'a'
    mtx2Param.combineValues = (47.4, 119.9, 11.6)
    mtx2Param.transposeMatrix = True
    mtx2 = Rmtxop(matrixFiles=[tempIll], outputFile=ill)
    mtx2.rmtxopParameters = mtx2Param
    if calcDict['DCCoeff']:
        mtx2.execute()

    # Step3: Generate direct daylight coefficients for normal sky-matrix using rfluxmtx.
    rfluxPara = RfluxmtxParameters()
    rfluxPara.irradianceCalc = True
    rfluxPara.ambientAccuracy = 0.01
    rfluxPara.ambientDivisions = 20000
    rfluxPara.ambientBounces = 1
    rfluxPara.limitWeight = 1E-7
    rfluxPara.ambientResolution = 10000


    rflux = Rfluxmtx()
    rflux.sender = '-'
    skyFile = rflux.defaultSkyGround(skyDomeFile, skyType='r%s' % reinhartPatches)
    rflux.receiverFile = skyDomeFile
    rflux.rfluxmtxParameters = rfluxPara
    rflux.radFiles = sceneData
    rflux.samplingRaysCount = 1

    rflux.pointsFile = pointsFile
    rflux.outputMatrix = dcCoeffMatrixDirect
    if calcDict['DirectDCCoeff']:
        rflux.execute()

    tempDirectIll = os.path.join(folderForCalculations, 'tempDirect.ill')
    illDirect = os.path.join(folderForCalculations, 'IlluminanceDirect.ill')

    dct = Dctimestep()
    dct.daylightCoeffSpec = dcCoeffMatrixDirect
    dct.skyVectorFile = skyMatrixDirect
    dct.outputFile = tempDirectIll
    if calcDict['DCCoeff']:
        dct.execute()



    mtx2Param = RmtxopParameters()
    mtx2Param.outputFormat = 'a'
    mtx2Param.combineValues = (47.4, 119.9, 11.6)
    mtx2Param.transposeMatrix = True
    mtx2 = Rmtxop(matrixFiles=[tempDirectIll], outputFile=illDirect)
    mtx2.rmtxopParameters = mtx2Param
    if calcDict['DirectDCCoeff']:
        mtx2.execute()

    solarDiscPath = os.path.join(folderForCalculations,'solarDiscs.rad')
    sunListPath = os.path.join(folderForCalculations,'sunList.txt')
    sunMatrixPath = os.path.join(folderForCalculations,'sunMatrix.mtx')
    #Calculate direct only ill files.
    directSunIll = os.path.join(folderForCalculations,'directSunIll.ill')

    if calcDict['DirectSun']:
        sunOnlyIll = calcDirectIlluminance(epwFile=epwFile, solarDiscPath=solarDiscPath, sunListPath=sunListPath,
                                           sunMatrixPath=sunMatrixPath,materialFile=materialFile,geometryFiles=geometryFiles,
                                           pointsFile=pointsFile, folderForCalculations=folderForCalculations,
                                           outputIllFilePath=directSunIll)

    #Instantiate matrices for subtraction and addition.
    finalMatrix = Rmtxop()

    #std. dc matrix.
    dcMatrix = RmtxopMatrix()
    dcMatrix.matrixFile = ill

    #direct dc matrix. -1 indicates that this one is being subtracted from dc matrix.
    dcDirectMatrix = RmtxopMatrix()
    dcDirectMatrix.matrixFile = illDirect
    dcDirectMatrix.scalarFactors = [-1]

    #Sun coefficient matrix.
    sunCoeffMatrix = RmtxopMatrix()
    sunCoeffMatrix.matrixFile = directSunIll

    #combine the matrices together. Sequence is extremely important
    finalMatrix.rmtxopMatrices  = [dcMatrix,dcDirectMatrix,sunCoeffMatrix]
    finalMatrix.outputFile = outputIllFilePath

    #Done!
    finalMatrix.execute()



    return outputIllFilePath


if __name__ == "__main__":

    os.chdir(os.path.dirname(os.getcwd()))
    epw = 'tests/assets/phoenix.epw'
    sunRad = 'tests/assets/phoenixSunPath.rad'

    sunList = 'tests/assets/phoenixList.txt'
    sunMtx = 'tests/assets/phooenixMtx.mtx'

    materialFile = r'tests/assets/material.rad'
    geometryFiles = r'tests/assets/geoSouth.rad'
    pointsFile = r'tests/assets/2x2.pts'

    calcFolder = r'tests/ASEtest'
    outputFilePath = r'tests/ASEtest/test.ill'





    improvedDCcalc(epwFile=epw,  materialFile=materialFile, geometryFiles=geometryFiles, pointsFile=pointsFile,
                   folderForCalculations=calcFolder, outputIllFilePath=outputFilePath,
                   calcDict={'skyVectors': False, 'DirectDCCoeff': False, 'DCCoeff': False, 'DirectSun': False})
