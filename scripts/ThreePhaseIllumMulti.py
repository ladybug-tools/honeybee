# coding=utf-8
"""
Date: 11/23/2016
By: Sarith Subramaniam (sariths)
Subject: Gridpoint based implementation of 3 Phase method using native Radiance
         binary files only. This time with multiple window groups.
Purpose: Prototype for showing illuminance calculations using 3 Phase.
Keywords: Radiance, Grid-Based, Illuminance, WindowGroups.
"""

import os
import sys
import glob

if 'honeybee' not in sys.modules:
    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from honeybee.radiance.parameters.rfluxmtx import RfluxmtxParameters
from honeybee.radiance.command.rfluxmtx import Rfluxmtx
from honeybee.radiance.command.epw2wea import Epw2wea
from honeybee.radiance.command.gendaymtx import Gendaymtx, GendaymtxParameters
from honeybee.radiance.command.dctimestep import Dctimestep
from honeybee.radiance.command.genskyvec import Genskyvec
from honeybee.radiance.command.gensky import Gensky
from honeybee.radiance.command.rmtxop import Rmtxop, RmtxopParameters
from honeybee import config

config.perlExePath = r'C:\Program Files\OpenStudio 1.13.0\strawberry-perl-5.16.2.1-32bit-portable-reduced\perl\bin\perl'

def run3phaseMulti(pointsFile, outputIllName, windowConfig=(), epwFile=None,
                   skyFile=None, geometryFile=None, materialFile=None,
                   reuseVmtx=True, reuseSkyVector=True, reuseDmtx=True,
                   skyDescr=1, klemsForVmtx='kf',
                   vmtxParam=None, dmtxParam=None, TransposeAnnualResults=True,
                   skyVectorParam=None):
    """
    Notes:
        1. It is assumed that the surfaces used for the vmtx are inward facing .i.e they
            need not be flipped.
        2. It is also assumed that the surfaces used for vmtx already have a glow modifier
            assigned to them.
    Args:

        outputIllName: Name of the file to which the results should be written.
        windowConfig: A tuple containing the windowGroupGeometry,
            the direction of the surface Normal, the corresponding T matrix XML and an
            option to include or exclude the results from the windowgroup in the
            calculation. A typical option will be something like ('glazing.rad','+Z',
            'blinds.xml',True), specifying that the radiance geometry 'glazing.rad', whose
            direction normal faces +Z will be used for the calculation of that particular
            V matrix. 'blinds.xml' indicates the XML file that will be used as T matrix
            for that window group and True indicates that this window group will be
            considered for the calculations.

        epwFile: epwFile corresponding to a particular location. If epwFile and skyFile
            are provided, the option for epwFile will be prioritized .i.e. the calculation
            will be annual.
        skyFile: An input from gensky or gendaylit for creating a point-in-time sky vector.
        geometryFile: Geometry for All the files in the calculation except the ones for
            the glazing.
        materialFile: Materials for all the geometry described in the geometryFile input.
        reuseVmtx: A boolean value for specifying if the Vmtx needs to be recalculated if
            it is already present.
        reuseDmtx: A boolean value for specifying if the Dmtx needs to be recalculated.
        reuseSkyVector: A boolean value for specifying if sky vector needs to be recalculated.
        pointsFile: The file containing the grid points that will be used for illumiance
            calcuations.
        skyDescr: An integer specifying the sky descretization value to be considered for
            generating the sky matrix. The values (number, skypataches)corresponding to
            different sky descretizations are : (1, 145),(2,577),(3,1297),(4,2305),
            (5,3601),(6,5185). Higher discretizations equal higher values.
        klemsForVmtx: The klems basis to be considered for sampling the vmtx. Default value
         is 'kf'
        vmtxParam: Calculation parameters corresponding to the V matrix. This should be
            an instance of the class RfluxParameters. If not specified, a default value
            will be assigned.
        dmtxParam: Calculation parameters corresponding to the D matrix. This should be
            an instance of the class RfluxParameters. If not specified, a default value
            will be assigned.
        TransposeAnnualResults: A boolean value, which if set to True, will transpose
         the results of an annual calculation as per the 8760 lines format.

    Returns:

    """

    def createWinGroupReceivers(surfaceFile, surfaceNormal, klemsBasis):
        # remove the + or - sign if specified.
        surfaceNormal = surfaceNormal[-1] if len(surfaceNormal) > 1 else surfaceNormal
        hemiUp = "+Z" if surfaceNormal.lower() in "xy" else "+X"

        # check if there is a glow material assigned in the file.
        # retrieve the first polygon surface for assigning rfluxmtxParameters.
        surfaceStringNoComments = ''
        with open(surfaceFile) as surfaceData:
            for lines in surfaceData:
                if not lines.strip().startswith("#"):
                    surfaceStringNoComments += lines

        surfaceStringNoComSplit = surfaceStringNoComments.split()
        assert surfaceStringNoComSplit[1] == 'glow',\
            'It appears that the glow material has not been applied to this surface.This' \
            ' is essential for the Three Phase Method. '
        firstPolyPosition = surfaceStringNoComSplit.index('polygon')
        surfaceName = surfaceStringNoComSplit[firstPolyPosition - 1]
        rflux = Rfluxmtx()
        receiverParam = rflux.ControlParameters(hemiType=klemsBasis,
                                                hemiUpDirection=hemiUp)
        receiverFile = rflux.addControlParameters(surfaceFile,
                                                  {surfaceName: receiverParam})
        return receiverFile

    def calcVmtx(surfaceFile, receiverFile, reuse, vmtxParam, pointsFile,
                 materialFile, geometryFile):

        vmtxFile = os.path.join('temp', os.path.splitext(surfaceFile)[0] + '.vmtx')
        if os.path.exists(vmtxFile) and reuse:
            return vmtxFile

        if vmtxParam:
            assert isinstance(vmtxParam, RfluxmtxParameters),\
                'The input for vmtxParam must be an instance of RfluxmtxParamters. ' \
                'The current input is an instance of %s' % (type(vmtxParam))
        else:
            vmtxParam = RfluxmtxParameters()
            vmtxParam.irradianceCalc = True
            vmtxParam.ambientAccuracy = 0.1
            vmtxParam.ambientBounces = 10
            vmtxParam.ambientDivisions = 65536
            vmtxParam.limitWeight = 1E-5

        rflux = Rfluxmtx()
        rflux.receiverFile = receiverFile
        rflux.rfluxmtxParameters = vmtxParam
        rflux.pointsFile = pointsFile
        rflux.sender = '-'
        rflux.outputMatrix = vmtxFile
        rflux.radFiles = [materialFile, geometryFile]
        print (rflux.toRadString())
        rflux.execute()
        return vmtxFile

    def calcDmtx(surfaceFile, senderFile, reuse, skyDescr, dmtxParam,
                 materialFile, geometryFile):

        dmtxFile = os.path.join('temp', os.path.splitext(surfaceFile)[0] + '.dmtx')
        if os.path.exists(dmtxFile) and reuse:
            return dmtxFile

        if dmtxParam:
            assert isinstance(dmtxParam, RfluxmtxParameters), \
                'The input for vmtxParam must be an instance of RfluxmtxParamters. ' \
                'The current input is an instance of %s' % (type(dmtxParam))
        else:
            dmtxParam = RfluxmtxParameters()
            dmtxParam.ambientAccuracy = 0.1
            dmtxParam.ambientBounces = 2
            dmtxParam.ambientDivisions = 1024
            dmtxParam.limitWeight = 1E-5

        rflux2 = Rfluxmtx()
        rflux2.samplingRaysCount = 1000
        rflux2.sender = senderFile
        skyFile = rflux2.defaultSkyGround(r'temp/rfluxSky.rad', skyType="r%s" % skyDescr)
        rflux2.receiverFile = skyFile
        rflux2.rfluxmtxParameters = dmtxParam
        rflux2.radFiles = [materialFile, geometryFile]
        rflux2.outputMatrix = dmtxFile
        rflux2.execute()

        return dmtxFile

    def calcSkyVector(skyDescr, epwFile=None, skyFile=None, reuse=True, skyVectorParam=None):
        assert epwFile or skyFile,\
            'Either an epwFile or a skyFile need to be provided for the skyVector to' \
            'be calculated.'

        if epwFile and os.path.exists(epwFile):
            epwName = os.path.split(epwFile)[1]
            skyMtxName = os.path.splitext(epwName)[0] + '%s.smx' % skyDescr
            weaName = os.path.splitext(epwFile)[0] + '.wea'
            if os.path.exists(skyMtxName) and reuse:
                return skyMtxName

            weaFile = Epw2wea(epwFile=epwFile, outputWeaFile=weaName)
            weaFile.execute()

            if skyVectorParam:
                assert isinstance(skyVectorParam, GendaymtxParameters),\
                    'The input for skyVectorParam must be an instance of GendaymtxParameters.'
                gendayParam = skyVectorParam
            else:
                gendayParam = GendaymtxParameters()

            gendayParam.skyDensity = skyDescr

            genday = Gendaymtx(weaFile=weaName, outputName=skyMtxName)
            genday.gendaymtxParameters = skyVectorParam
            genday.execute()

            return skyMtxName
        elif skyFile and os.path.exists(skyFile):
            skyMtxName = os.path.splitext(skyFile)[0] + '%s.smx' % skyDescr

            if os.path.exists(skyMtxName) and reuse:
                return skyMtxName
            genskv = Genskyvec()
            genskv.inputSkyFile = skyFile
            genskv.skySubdivision = skyDescr
            genskv.outputFile = skyMtxName
            genskv.execute()
            return skyMtxName

        else:
            raise Exception('The input path for the skyFile or epwFile are not valid.')

    # generate receiver surfaces for all window groups..This is not an intensive process.
    receiverFiles = [createWinGroupReceivers(win['windowSurface'],
                                             win['surfaceNormal'],
                                             klemsForVmtx) for win in windowConfig]

    # create the skyVector.
    skyVector = calcSkyVector(skyDescr=skyDescr, epwFile=epwFile, skyFile=skyFile,
                              reuse=reuseSkyVector, skyVectorParam=skyVectorParam)

    # create V and D matrices corresponding to each window Group.

    matrixFilesForResult = []
    resultFiles = 0
    for idx, recFile in enumerate(receiverFiles):

        vmtxFile = calcVmtx(
            windowConfig[idx]['windowSurface'], recFile, reuse=reuseVmtx,
            vmtxParam=vmtxParam, pointsFile=pointsFile, materialFile=materialFile,
            geometryFile=geometryFile)

        dmtxFile = calcDmtx(windowConfig[idx]['windowSurface'], senderFile=recFile,
                            skyDescr=skyDescr, dmtxParam=dmtxParam,
                            materialFile=materialFile, geometryFile=geometryFile,
                            reuse=reuseDmtx)

        if windowConfig[idx]['includeInCalc']:
            windowName = os.path.splitext(windowConfig[idx]['windowSurface'])[0] + 'Res.tmp'
            dctResult = os.path.join('temp', windowName)
            dct = Dctimestep()
            dct.dmatrixFile = dmtxFile
            dct.vmatrixSpec = vmtxFile
            dct.skyVectorFile = skyVector
            dct.tmatrixFile = windowConfig[idx]['tMatrix']
            dct.outputFileName = dctResult
            dct.execute()
            matrixFilesForResult.append(dctResult)

            resultFiles += 1
    assert resultFiles, 'None of the Window Groups were chosen for calculating the results !'

    # add up values into a single tmp file
    rmtxAdd = Rmtxop()
    rmtxAdd.matrixFiles = matrixFilesForResult
    rmtxAdd.outputFile = os.path.splitext(outputIllName)[0] + '.tmp'
    rmtxAdd.execute()

    # convert r g b to illuminance
    rmtResParam = RmtxopParameters()
    rmtResParam.combineValues = (47.4, 119.9, 11.6)
    rmtResParam.outputFormat = 'a'
    rmtResParam.transposeMatrix = TransposeAnnualResults

    rmtxRes = Rmtxop()
    rmtxRes.matrixFiles = [rmtxAdd.outputFile]
    rmtxRes.outputFile = outputIllName
    rmtxRes.rmtxopParameters = rmtResParam
    rmtxRes.execute()

    return outputIllName


if __name__ == "__main__":
    os.chdir(r'../tests')
    # get epwFile and xmlFile
    epwFile = os.path.abspath(glob.glob('assets/*.epw')[0])
    xmlFiles = map(os.path.abspath, glob.glob('assets/*.xml'))

    os.chdir('room2')
    if not os.path.exists('temp'):
        os.mkdir('temp')

    if True:
        gensk = Gensky()
        gensk.monthDayHour = (11, 11, 11)
        gensk.outputFile = 'temp/sky.rad'
        gensk.execute()
        skyFile = 'temp/sky.rad'
    else:
        skyFile = None

    # creating WindowConfigurations.
    win1 = {'windowSurface': 'glazingEast.rad',
            'surfaceNormal': '+X',
            'tMatrix': xmlFiles[0],
            'includeInCalc': True}

    win2 = {'windowSurface': 'glazingSkylight.rad',
            'surfaceNormal': '+Z',
            'tMatrix': xmlFiles[0],
            'includeInCalc': True}

    win3 = {'windowSurface': 'glazingSouth.rad',
            'surfaceNormal': '+Y',
            'tMatrix': xmlFiles[0],
            'includeInCalc': True}

    run3phaseMulti(windowConfig=(win1, win2, win3), epwFile=None, skyFile=skyFile,
                   geometryFile='geometry.rad', materialFile='materials.rad',
                   reuseVmtx=True, reuseSkyVector=True, reuseDmtx=True,
                   pointsFile='points.txt', skyDescr=1, klemsForVmtx='kf',
                   vmtxParam=None, dmtxParam=None, TransposeAnnualResults=True,
                   skyVectorParam=None, outputIllName=r'temp/3ph1.ill')
