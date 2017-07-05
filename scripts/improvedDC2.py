# coding=utf-8
"""
Date: 05/28/2017
By: Sarith Subramaniam (@sariths)
Subject: Improved daylight coefficient method.
Purpose: -
Keywords: Radiance, Grid-Based, Illuminance
"""
from __future__ import division

import sys
sys.path.append(r"C:\Users\Mostapha\Documents\code\ladybug-tools\ladybug")
sys.path.append(r"C:\Users\Mostapha\Documents\code\ladybug-tools\honeybee")

from honeybee.radiance.parameters.rfluxmtx import RfluxmtxParameters
from honeybee.radiance.command.rfluxmtx import Rfluxmtx
from honeybee.radiance.command.epw2wea import Epw2wea
from honeybee.radiance.command.gendaymtx import Gendaymtx, GendaymtxParameters
from honeybee.radiance.command.rmtxop import Rmtxop, RmtxopParameters, RmtxopMatrix
from honeybee.radiance.command.xform import Xform, XformParameters
import time
import warnings
import os
from sunPathIlluminance import calcDirectIlluminance
from honeybee.radiance.command.dctimestep import Dctimestep, DctimestepParameters


def improvedDCcalc(epwFile, materialFile, geometryFiles, pointsFile,
                   folderForCalculations, outputIllFilePath, glazingGeometry=None,
                   reinhartPatches=1, ambBounces=5, ambDiv=5000,
                   limitWt=0.0002, calcDict={'skyVectors': True, 'DirectDCCoeff': True,
                                             'DCCoeff': True, 'DirectSun': True},
                   cleanUpTempFiles=True):
    """
    Args:
        epwFile: Epw file path.
        materialFile: Path for a single material file.
        geometryFiles: One or more geometry files.
        pointsFile: Path for poitns file
        folderForCalculations: Folder for storing intermediate files.
        outputIllFilePath:
        reinhartPatches: Default is 1.
        calcDict: This is useful for selectively running different parts of the
            simulation.
        ambBounces: Ambient bounces. Defaults to 5
        ambDiv: Ambient divisions. Defaults to 5000.
        limitWt: Limit weight. Defaults to 0.0002
        cleanUpTempFiles: Delete all the temporary files that were created during the
            calculations.
    Returns: The path of the illuminance file generated through the calculations.

    """

    # a sad logging hack
    statusMsg = lambda msg: "\n%s:%s\n%s\n" % (time.ctime(), msg, "*~" * 25)

    blackMaterial = "void plastic black 0 0 5 0 0 0 0 0"

    if limitWt > (1 / ambDiv):
        warnings.warn("The value for limitWt(%s) should be set to a value equal to or "
                      "less (%s) which is 1/ambDiv(%s)" % (limitWt, 1 / ambDiv, ambDiv))

    # crate a tempfolder inside the folderForCalculations.
    tmpFolder = os.path.join(folderForCalculations, 'tmp')
    if not os.path.exists(tmpFolder):
        os.mkdir(tmpFolder)

    weaFilePath = os.path.join(tmpFolder,
                               os.path.splitext(os.path.split(epwFile)[1])[0] + '.wea')

    weaFile = Epw2wea(epwFile=epwFile, outputWeaFile=weaFilePath)
    weaFile.execute()

    # Calculate complete sky matrix.
    skyMatrix = os.path.join(tmpFolder, 'skyMatrix.mtx')
    gendayParam = GendaymtxParameters()
    gendayParam.skyDensity = reinhartPatches
    genday = Gendaymtx(weaFile=weaFilePath, outputName=skyMatrix)
    genday.gendaymtxParameters = gendayParam
    if calcDict['skyVectors']:
        print(genday.toRadString())
        genday.execute()

    # Calculate direct only matrix.
    skyMatrixDirect = os.path.join(tmpFolder, 'skyMatrixDirect.mtx')
    gendayParam = GendaymtxParameters()
    gendayParam.skyDensity = reinhartPatches
    gendayParam.onlyDirect = True
    genday = Gendaymtx(weaFile=weaFilePath, outputName=skyMatrixDirect)
    genday.gendaymtxParameters = gendayParam
    if calcDict['skyVectors']:
        print(genday.toRadString())
        genday.execute()

    skyDomeFile = os.path.join(tmpFolder, 'rfluxSky.rad')
    dcCoeffMatrix = os.path.join(tmpFolder, 'dc.mtx')
    dcCoeffMatrixDirect = os.path.join(tmpFolder, 'dcDirect.mtx')

    blackMaterial = os.path.join(tmpFolder, 'black.mat')

    with open(blackMaterial, 'w') as blackMat:
        blackMat.write("void plastic black 0 0 5 0 0 0 0 0")

    sceneData = [materialFile]
    sceneDataBlack = [blackMaterial]

    geometryData = []

    # Append if single, extend if multiple
    if isinstance(geometryFiles, basestring):
        geometryData.append(geometryFiles)
    elif isinstance(geometryFiles, (tuple, list)):
        geometryData.extend(geometryFiles)

    sceneData = sceneData + geometryData

    xfrPara = XformParameters()
    xfrPara.modReplace = 'black'

    # Note: Xform has this thing it only works well if the paths are absolute.
    blackGeometry = os.path.join(tmpFolder, 'blackGeometry.rad')
    xfr = Xform()
    xfr.xformParameters = xfrPara
    xfr.radFile = geometryData
    xfr.outputFile = blackGeometry
    xfr.execute()

    # Material file added in the end with the assumption that the material props for the
    # glazing are defined in the material file. As Radiance parses scene data in a
    # strictly linear fashion, even if the material for glazing is defined inside
    # the glazing geometry, it will still be fine.
    sceneDataBlack = sceneDataBlack + [blackGeometry] + [materialFile]

    if isinstance(glazingGeometry, basestring):
        sceneData.append(glazingGeometry)
        sceneDataBlack.append(glazingGeometry)

    elif isinstance(glazingGeometry, (tuple, list)):
        sceneData.extend(glazingGeometry)
        sceneDataBlack.extend(glazingGeometry)

    # Step2: Generate daylight coefficients for normal sky-matrix using rfluxmtx.
    rfluxPara = RfluxmtxParameters()
    rfluxPara.irradianceCalc = True
    rfluxPara.ambientDivisions = ambDiv
    rfluxPara.ambientBounces = ambBounces
    rfluxPara.limitWeight = limitWt

    rflux = Rfluxmtx()
    rflux.sender = '-'
    skyFile = rflux.defaultSkyGround(skyDomeFile, skyType='r%s' % reinhartPatches)
    rflux.receiverFile = skyDomeFile
    rflux.rfluxmtxParameters = rfluxPara
    rflux.radFiles = sceneData
    rflux.samplingRaysCount = 1

    rflux.pointsFile = pointsFile
    rflux.outputMatrix = dcCoeffMatrix
    if calcDict['DCCoeff']:
        print(rflux.toRadString())
        rflux.execute()

    tempIll = os.path.join(tmpFolder, 'temp.ill')
    ill = os.path.join(tmpFolder, 'Illuminance.ill')

    dct = Dctimestep()
    dct.daylightCoeffSpec = dcCoeffMatrix
    dct.skyVectorFile = skyMatrix
    dct.outputFile = tempIll
    if calcDict['DCCoeff']:
        print(dct.toRadString())
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
    rfluxPara.ambientDivisions = ambDiv
    rfluxPara.ambientBounces = 1
    rfluxPara.limitWeight = limitWt

    rflux = Rfluxmtx()
    rflux.sender = '-'
    skyFile = rflux.defaultSkyGround(skyDomeFile, skyType='r%s' % reinhartPatches)
    rflux.receiverFile = skyDomeFile
    rflux.rfluxmtxParameters = rfluxPara
    rflux.radFiles = sceneDataBlack
    rflux.samplingRaysCount = 1

    rflux.pointsFile = pointsFile
    rflux.outputMatrix = dcCoeffMatrixDirect
    if calcDict['DirectDCCoeff']:
        rflux.execute()

    tempDirectIll = os.path.join(tmpFolder, 'tempDirect.ill')
    illDirect = os.path.join(tmpFolder, 'IlluminanceDirect.ill')

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

    solarDiscPath = os.path.join(tmpFolder, 'solarDiscs.rad')
    sunListPath = os.path.join(tmpFolder, 'sunList.txt')
    sunMatrixPath = os.path.join(tmpFolder, 'sunMatrix.mtx')
    # Calculate direct only ill files.
    directSunIll = os.path.join(tmpFolder, 'directSunIll.ill')

    if calcDict['DirectSun']:
        calcDirectIlluminance(
            epwFile=epwFile, solarDiscPath=solarDiscPath,
            sunListPath=sunListPath, sunMatrixPath=sunMatrixPath,
            materialFile=blackMaterial, geometryFiles=sceneDataBlack,
            pointsFile=pointsFile,
            folderForCalculations=folderForCalculations,
            outputIllFilePath=directSunIll
        )

    # Instantiate matrices for subtraction and addition.
    finalMatrix = Rmtxop()

    # std. dc matrix.
    dcMatrix = RmtxopMatrix()
    dcMatrix.matrixFile = ill

    # direct dc matrix. -1 indicates that this one is being subtracted from dc matrix.
    dcDirectMatrix = RmtxopMatrix()
    dcDirectMatrix.matrixFile = illDirect
    dcDirectMatrix.scalarFactors = [-1]

    # Sun coefficient matrix.
    sunCoeffMatrix = RmtxopMatrix()
    sunCoeffMatrix.matrixFile = directSunIll

    # combine the matrices together. Sequence is extremely important
    finalMatrix.rmtxopMatrices = [dcMatrix, dcDirectMatrix, sunCoeffMatrix]
    finalMatrix.outputFile = outputIllFilePath

    # Done!
    finalMatrix.execute()

    return outputIllFilePath


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))

    epw = os.path.join(os.getcwd(), 'honeybee/tests/room', 'test.epw')
    sunRad = 'honeybee/tests/assets/phoenix.anlm'

    sunList = 'honeybee/tests/assets/phoenix.sun'
    sunMtx = 'honeybee/tests/assets/phoenix_dir.mtx'

    materialFile = r'honeybee/tests/room/room.mat'
    geometryFiles = os.path.abspath('honeybee/tests/room/room.rad')
    glazingGeometry = r'honeybee/tests/room/glazing.rad'
    pointsFile = os.path.abspath(r'honeybee/tests/room/indoor_points.pts')

    calcFolder = os.path.abspath(r'honeybee/tests/room')
    outputFilePath = r'honeybee/tests/room/test.ill'

    improvedDCcalc(epwFile=epw, materialFile=materialFile, geometryFiles=geometryFiles,
                   pointsFile=pointsFile,
                   folderForCalculations=calcFolder, outputIllFilePath=outputFilePath,
                   glazingGeometry=glazingGeometry,
                   calcDict={'skyVectors': True,
                             'DirectDCCoeff': True,
                             'DCCoeff': True,
                             'DirectSun': True})
