# coding=utf-8
"""
Date: 03/28/2017
By: Sarith Subramaniam (sariths)
Subject: Calculate ASE
Purpose: Script for calculating ASE and ASE only.
Keywords: Radiance, Grid-Based, Illuminance
"""

from __future__ import division, print_function
import sys
sys.path.extend((r'C:\Users\Mostapha\Documents\code\ladybug-tools\honeybee',
                 r'C:\Users\Mostapha\Documents\code\ladybug-tools\ladybug'))
import os
from itertools import izip
from ladybug.analysisperiod import AnalysisPeriod
from sunPathIlluminance import calcDirectIlluminance


def ase(epwFile, solarDiscPath, sunListPath, sunMatrixPath, materialFile,
        geometryFiles, pointsFile, folderForCalculations, outputIllFilePath,
        overWriteExistingFiles=True, dateIntervalForASE=((1, 1), (12, 31)),
        hourIntervalForASE=(8, 17), illumForASE=1000, hoursForASE=250,
        calcASEptsSummary=True):
    """ Calculate ASE.

    Args:
        epwFile: Epw file path.
        solarDiscPath: A string specifiying the file path for the solar disc that
            will be written.
        sunListPath: A string specifiying the file path for list of suns.
        sunMatrixPath: A string specifiying the file path for the sun matrix.
        materialFile: A single materials file path. Should already exist.
        geometryFiles: One or more geometry files.
        pointsFile:
        folderForCalculations: Folder where all the intermediate files are to be stored.
        outputIllFilePath: The filepath where the output from the ase calculations
            is to be stored.
        overWriteExistingFiles: Set this to True to overwrite existing matrices.
            if the file exists, a warning will be issued.
        dateIntervalForASE:
        hourIntervalForASE:
        illumForASE: Default 1000 lux as per lm-83-12
        hoursForASE: default 250 hours as per lm-83-12
        calcASEptsSummary:

    Returns:
    """

    stMonth, stDay = dateIntervalForASE[0]
    endMonth, endDay = dateIntervalForASE[1]
    stHour, endHour = hourIntervalForASE

    HOYList = AnalysisPeriod(stMonth=stMonth, endMonth=endMonth, stDay=stDay,
                             endDay=endDay, stHour=stHour, endHour=endHour).intHOYs

    illFile = calcDirectIlluminance(epwFile=epwFile, solarDiscPath=solarDiscPath,
                                    sunListPath=sunListPath,
                                    sunMatrixPath=sunMatrixPath,
                                    materialFile=materialFile,
                                    geometryFiles=geometryFiles,
                                    pointsFile=pointsFile,
                                    folderForCalculations=folderForCalculations,
                                    outputIllFilePath=outputIllFilePath,
                                    HOYList=HOYList,
                                    overWriteExistingFiles=overWriteExistingFiles)

    # get points Data
    pointsList = []
    with open(pointsFile)as pointsData:
        for lines in pointsData:
            if lines.strip():
                pointsList.append(map(float, lines.strip().split()[:3]))

    hourlyIlluminanceValues = []
    with open(illFile) as resData:
        for lines in resData:
            lines = lines.strip()
            if lines:
                try:
                    tempIllData = map(float, lines.split())
                    hourlyIlluminanceValues.append(tempIllData)
                except ValueError:
                    pass

    # As per IES-LM-83-12 ASE is the percent of sensors in the analysis area that are
    # found to be exposed to more than 1000lux of direct sunlight for more than 250hrs
    # per year. The present script allows user to define what the lux and hour value
    # should be.
    sensorIllumValues = izip(*hourlyIlluminanceValues)
    aseData = []
    for idx, sensor in enumerate(sensorIllumValues):
        x, y, z = pointsList[idx]
        countAboveThreshold = len([val for val in sensor if val > illumForASE])
        aseData.append([x, y, z, countAboveThreshold])

    sensorsWithHoursAboveLimit = [hourCount for x, y, z, hourCount in aseData if
                                  hourCount > hoursForASE]

    percentOfSensors = len(sensorsWithHoursAboveLimit) / len(pointsList) * 100
    print("ASE RESULT: Percent of sensors above %sLux for more than %s hours = %s%%"
          % (illumForASE, hoursForASE, percentOfSensors))

    if calcASEptsSummary:
        print("ASE RESULT: Location of sensors and # of hours above threshold of %sLux\n" % illumForASE)
        print("%12s %12s %12s %12s" % ('xCor', 'yCor', 'zCor', 'Hours'))
        for x, y, z, countAboveThreshold in aseData:
            print("%12.4f %12.4f %12.4f %12d" % (x, y, z, countAboveThreshold))


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

    ase(epwFile=epw, solarDiscPath=sunRad, sunListPath=sunList, sunMatrixPath=sunMtx,
        materialFile=materialFile, geometryFiles=geometryFiles, pointsFile=pointsFile,
        folderForCalculations=calcFolder, outputIllFilePath=outputFilePath)
