# coding=utf-8
"""
Date: 03/28/2017
By: Sarith Subramaniam (sariths)
Subject: Script for calculating illuminance from sunpath
Purpose: This can be used for ASE and improved Daylight Coefficient simulations.
Keywords: Radiance, Grid-Based, Illuminance
"""
from __future__ import division, print_function
from analemma import analemma as analemmacalculator
import time
import os
from ladybug.analysisperiod import AnalysisPeriod
from honeybee.radiance.command.oconv import Oconv
from honeybee.radiance.command.rcontrib import Rcontrib, RcontribParameters
from honeybee.radiance.command.dctimestep import Dctimestep
from honeybee.radiance.command.rmtxop import RmtxopParameters, Rmtxop
import warnings

HOYList = AnalysisPeriod(stMonth=1, endMonth=12, stDay=1,
                         endDay=31, stHour=8, endHour=17)


def calcDirectIlluminance(
        epwFile, analemmaPath, sunListPath, sunMatrixPath,
        materialFile, geometryFiles, pointsFile, folderForCalculations,
        outputIllFilePath, HOYList=range(8760),
        overWriteExistingFiles=True):
    """
    Calculate direct illuminance from the Sun.
    Args:
        epwFile: EPW file path.
        solarDiscPath:
        sunListPath:
        sunMatrixPath:
        materialFile: A single material file.
        geometryFiles: One or more geometry files.
        pointsFile: A points file in Daysim compatible format.
        folderForCalculations: A folder where all the intermediate files can be stored.
        outputIllFilePath:
        HOYList:
        overWriteExistingFiles:

    Returns:

    """

    # a sad logging hack
    statusMsg = lambda msg: "\n%s:%s\n%s\n" % (time.ctime(), msg, "*~" * 25)

    # over-write warning.
    def overWriteWarning(filePath, overWriteExistingFiles=overWriteExistingFiles):
        if os.path.exists(filePath):
            if not overWriteExistingFiles:
                raise Exception(
                    "The file %s already exists. Set the variable overWriteExistingFiles"
                    "to True to overWrite this and other files." % filePath)
            else:
                msg = "The file %s already existed and was overwritten" % filePath
                warnings.warn(msg)

    statusMsg('Generating sunpath and sunmatrix')
    analemmaPath, sunListPath, sunMatrixPath = analemmacalculator(
        epwFile=epwFile, sunDiscRadPath=analemmaPath, sunListPath=sunListPath,
        solarRadiationMatrixPath=sunMatrixPath, HOYlist=HOYList)

    sceneData = [materialFile]
    # Append if single, extend if multiple
    if isinstance(geometryFiles, basestring):
        sceneData.append(geometryFiles)
    elif isinstance(geometryFiles, (tuple, list)):
        sceneData.extend(geometryFiles)

    octreeFile = os.path.join(folderForCalculations, 'solar.oct')
    # overWriteWarning(octreeFile)

    statusMsg('Creating octree')
    octree = Oconv()
    octree.sceneFiles = sceneData + [analemmaPath]
    octree.outputFile = octreeFile
    octree.execute()

    statusMsg('Creating sun coefficients')
    dcFile = os.path.join(folderForCalculations, 'sunCoeff.dc')
    overWriteWarning(dcFile)

    tmpIllFile = os.path.join(folderForCalculations, 'illum.tmp')
    overWriteWarning(tmpIllFile)

    rctPara = RcontribParameters()
    rctPara.ambientBounces = 0
    rctPara.directJitter = 0
    rctPara.directCertainty = 1
    rctPara.directThreshold = 0
    rctPara.modFile = sunListPath
    rctPara.irradianceCalc = True

    rctb = Rcontrib()
    rctb.octreeFile = octreeFile
    rctb.outputFile = dcFile
    rctb.pointsFile = pointsFile
    rctb.rcontribParameters = rctPara

    rctb.execute()

    statusMsg('Performing matrix multiplication between the coefficients'
              ' and the sun matrix.')
    dct = Dctimestep()
    dct.daylightCoeffSpec = dcFile
    dct.skyVectorFile = sunMatrixPath
    dct.outputFile = tmpIllFile
    dct.execute()

    statusMsg('Transposing the matrix as per time-series and calculating illuminance.')
    mtx2Param = RmtxopParameters()
    mtx2Param.outputFormat = 'a'
    mtx2Param.combineValues = (47.4, 119.9, 11.6)
    mtx2Param.transposeMatrix = True
    mtx2 = Rmtxop(matrixFiles=[tmpIllFile], outputFile=outputIllFilePath)
    mtx2.rmtxopParameters = mtx2Param
    mtx2.execute()

    return outputIllFilePath


if __name__ == "__main__":

    os.chdir(os.path.dirname(os.getcwd()))
    epw = 'tests/assets/phoenix.epw'
    sunRad = 'tests/assets/phoenixSunPath.rad'
    # analemma(epw,sunRad)

    sunList = 'tests/assets/phoenixList.txt'
    sunMtx = 'tests/assets/phooenixMtx.mtx'

    materialFile = r'tests/assets/material.rad'
    geometryFiles = r'tests/assets/geoSouth.rad'
    pointsFile = r'tests/assets/2x2.pts'

    calcFolder = r'tests/ASEtest'
    outputFilePath = r'tests/ASEtest/test.ill'

    calcDirectIlluminance(
        epwFile=epw, analemmaPath=sunRad, sunListPath=sunList, sunMatrixPath=sunMtx,
        materialFile=materialFile, geometryFiles=geometryFiles, pointsFile=pointsFile,
        folderForCalculations=calcFolder, outputIllFilePath=outputFilePath
    )
