# coding=utf-8
"""
Date: 04/03/2017
By: Sarith Subramaniam (sariths)
Subject: Script for creating a radiance-based sun path
Purpose: Sunpath can be used for ASE, Improving Grid-based simulations etc.
Keywords: Radiance, Grid-Based, Illuminance
"""
from __future__ import division, print_function
from honeybee.radiance.command.gendaylit import Gendaylit, GendaylitParameters
from ladybug.epw import EPW
from ladybug.analysisperiod import DateTime
from subprocess import Popen, PIPE
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamH = logging.StreamHandler()
formatter = logging.Formatter('\n%(asctime)s: %(message)s\n')
streamH.setFormatter(formatter)
logger.addHandler(streamH)


def analemma(epwFile, sunDiscRadPath, sunListPath=None, solarRadiationMatrixPath=None,
             HOYlist=range(8760)):
    """Sun analemma calculator.

    This function can be used for multiple purposes. For just generating the
    sunDiscRadPath for visualizing physically-accurate sun positions, specify
    only that variable. For calculating ASE or for Daylight Coefficient
    calculations, specify the sunListPath and solarRadiationMatrixPath as well.

    Args:
        epwFile: A standard epw file containing 8760 data points. Hacked epws will
            also work but then the HOY input needs to be adjusted accordingly.
            Required input.
        sunDiscRadPath: The path for the rad file to which the Radiance definitions
            of solar discs will be written to.
        sunListPath: The path for the list of suns which is required for daylighting
            calculations.
        solarRadiationMatrixPath: The path for the matrix containing solar radiation.
        HOYlist: A list of hours of the year.

    Returns: Paths for sunDiscRadPath, sunListPath and solarRadiationMatrixPath

    usage:
        sunRad,sunList,sunMtx = analemma(epwFile,sunRad,...)
        And then to other processes.
    """

    if sunListPath or solarRadiationMatrixPath:
        assert sunListPath and solarRadiationMatrixPath,\
            'If either sunListPath (%s) or solarRadiationMatrixPath (%s) ' \
            'are specified, the other variable needs to be specified' \
            ' as well.' % (sunListPath, solarRadiationMatrixPath)

    logger.info('Starting calculations')

    monthDateTime = (DateTime.fromHoy(idx) for idx in HOYlist)

    epw = EPW(epwFile)
    latitude, longitude = epw.location.latitude, -epw.location.longitude
    meridian = -(15 * epw.location.timezone)

    # Create a directory for ASE test.

    # Defining these upfront so that this data may be used for validation without
    # rerunning calcs every time

    # instantiating classes before looping makes sense as it will avoid the same calls
    # over and over.
    genParam = GendaylitParameters()
    genParam.meridian = meridian
    genParam.longitude = longitude
    genParam.latitude = latitude

    genDay = Gendaylit()

    sunValues = []
    sunValuesHour = []

    logger.info('Calculating sun positions and radiation values')

    # We need to throw out all the warning values arising from times when sun isn't
    # present.
    # os.devnull serves that purpose.
    with open(os.devnull, 'w') as warningDump:
        for timeStamp in monthDateTime:
            month, day, hour = timeStamp.month, timeStamp.day, timeStamp.hour + 0.5
            dnr, dhr = epw.directNormalRadiation[timeStamp.intHOY], \
                epw.diffuseHorizontalRadiation[timeStamp.intHOY]

            if dnr + dhr == 0:
                # no need to run gendaylit as there is no radiation / sun
                continue

            genParam.dirNormDifHorzIrrad = (dnr, dhr)

            genDay.monthDayHour = (month, day, hour)
            genDay.gendaylitParameters = genParam
            gendayCmd = genDay.toRadString().split('|')[0]

            # run cmd, get results in the form of a list of lines.
            cmdRun = Popen(gendayCmd, stdout=PIPE, stderr=warningDump)
            data = cmdRun.stdout.read().split('\n')
            print(data)
            assert False
            # clean the output by throwing out comments and brightness functions.
            sunCurrentValue = []
            for lines in data:
                if not lines.strip().startswith("#"):
                    if "brightfunc" in lines:
                        break
                    if lines.strip():
                        sunCurrentValue.extend(lines.strip().split())

            # If a sun definition was captured in the last for-loop, store info.
            if sunCurrentValue and max(map(float, sunCurrentValue[6:9])):
                sunCurrentValue[2] = 'solar%s' % (len(sunValues) + 1)
                sunCurrentValue[9] = 'solar%s' % (len(sunValues) + 1)
                sunValues.append(sunCurrentValue)
                sunValuesHour.append(timeStamp.intHOY)

    numOfSuns = len(sunValues)

    logger.info('Writing sun definitions to disc')

    # create solar discs.
    with open(sunDiscRadPath, 'w') as solarDiscFile:
        solarDiscFile.write("\n".join([" ".join(sun) for sun in sunValues]))

    logger.info('Sun definitions are written to: %s' % sunDiscRadPath)

    if solarRadiationMatrixPath:
        # create list of suns.
        with open(sunListPath, 'w') as sunListPathData:
            sunListPathData.write(
                "\n".join(["solar%s" % (idx + 1) for idx in xrange(numOfSuns)])
            )

        # Start creating header for the sun matrix.
        fileHeader = ['#?RADIANCE']
        fileHeader += ['Sun matrix created by Honeybee']
        fileHeader += ['LATLONG= %s %s' % (latitude, -longitude)]
        fileHeader += ['NROWS=%s' % numOfSuns]
        fileHeader += ['NCOLS=%s' % len(HOYlist)]
        fileHeader += ['NCOMP=3']
        fileHeader += ['FORMAT=ascii']

        # Write the matrix to file.
        with open(solarRadiationMatrixPath, 'w') as sunMtx:
            sunMtx.write("\n".join(fileHeader) + '\n' + '\n')
            for idx, sunValue in enumerate(sunValues):
                sunRadList = ["0 0 0"] * len(HOYlist)
                sunRadList[sunValuesHour[idx]] = " ".join(sunValue[6:9])
                sunMtx.write("\n".join(sunRadList) + "\n" + "\n")

            # This last one is for the ground.
            sunRadList = ["0 0 0"] * len(HOYlist)
            sunMtx.write("\n".join(sunRadList))

    return sunDiscRadPath, sunListPath, solarRadiationMatrixPath


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.getcwd()))
    epw = os.path.join(os.getcwd(), 'honeybee/tests/room', 'test.epw')
    # epw = './tests/room/epws/USA_OH_Cleveland-Burke.Lakefront.AP.725245_TMY3.epw'
    sunRad = os.path.join(os.getcwd(), 'honeybee/tests/assets/phoenixSunPath.rad')
    sunList = os.path.join(os.getcwd(), 'honeybee/tests/assets/sunList.txt')
    sunMtx = os.path.join(os.getcwd(), 'honeybee/tests/assets/skyMtx.mtx')
    analemma(epw, sunRad, sunListPath=sunList, solarRadiationMatrixPath=sunMtx)
