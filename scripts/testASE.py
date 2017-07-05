from __future__ import division,print_function
from honeybee.radiance.command.gendaylit import Gendaylit,GendaylitParameters
from honeybee.radiance.command.oconv import Oconv
from honeybee.radiance.parameters.gridbased import GridBasedParameters
from honeybee.radiance.command.rtrace import Rtrace
from honeybee.radiance.command.rcontrib import Rcontrib,RcontribParameters
from honeybee.radiance.command.dctimestep import Dctimestep
from honeybee.radiance.command.rmtxop import RmtxopParameters,Rmtxop
from ladybug.wea import EPW
from ladybug.dt import DateTime
from subprocess import Popen,PIPE
import os
import time


def directSunCalcs(epwFile, materialFile, geometryFiles, pointsFile,
                   calcASE=True, calcASEptsSummary=True, illumForASE=1000,
                   hoursForASE=250, hoyForValidation=13,repeatValidationOnly=False):
    """

    Args:
        epwFile: path.
        materialFile: path.
        geometryFiles: path(s).
        pointsFile: path.
        calcASE: Boolean. If set to False, only raytrace and illuminance calcs will be
            performed.
        calcASEptsSummary: If set to True, will produce a summary of points and the number
            of hours for which they are above the value set for illumForASE. If set to
            False only the direct value of ASE (as specified by LM-83-12 will be calculated.)
        illumForASE: Illuminance for ASE. Has been set to a default of 1000 lux as per
            LM-83-12.
        hoursForASE: Hour-threshold for ASE. Has been set to a default of 250 hours as per
            LM-83-12. This option is only relevant if the the calcASEptsSummary option has
            been set to False. As otherwise, an entire list of hours will be produced regardless.
        hoyForValidation: A value between 0 to 8759 to check the annual results against an
            independent point-in-time ray-trace calc using rtrace. No validation will be
            performed if this value is set to None.
        repeatValidationOnly: Once the claculations have been run. Validation for more
            hours can be performed by setting this to True. Default is False.

    Returns: This function prints out. Does not return anything.

    """

    #a sad logging hack
    statusMsg = lambda msg: "\n%s:%s\n%s\n" % (time.ctime(),msg ,"*~"*25)

    print(statusMsg('Starting calculations'))

    sceneData=[materialFile]
    #Append if single, extend if multiple
    if isinstance(geometryFiles,basestring):
        sceneData.append(geometryFiles)
    elif isinstance(geometryFiles,(tuple,list)):
        sceneData.extend(geometryFiles)

    monthDateTime = [DateTime.fromHoy(idx) for idx in xrange(8760)]

    epw = EPW(epwFile)
    latitude, longitude = epw.location.latitude, -epw.location.longitude
    meridian = -(15 * epw.location.timezone)

    #Create a directory for ASE test.
    dirName = 'tests/ASEtest'
    if not os.path.exists(dirName):
        os.mkdir(dirName)
    #Defining these upfront so that this data may be used for validation without rerunning
    #calcs every time
    sunList = os.path.join(dirName, 'sunlist')
    sunDiscRadFile=os.path.join(dirName,'sunFile.rad')
    radiationMatrix=os.path.join(dirName,'sunRadiation.mtx')
    annualResultsFile=os.path.join(dirName,'illum.ill')

    if not repeatValidationOnly:
        # preCalcFiles = (sunList,sunDiscRadFile,radiationMatrix,annualResultsFile)
        # for files in preCalcFiles:
        #     assert os.path.exists(files),'Precalculated data cannot be used as the file ' \
        #                                  '%s, which is required for calculations cannot be' \
        #                                  'found.'



        #instantiating classes before looping makes sense as it will avoid the same calls over
        #   and over.
        genParam = GendaylitParameters()
        genParam.meridian=meridian
        genParam.longitude=longitude
        genParam.latitude=latitude

        genDay = Gendaylit()


        sunValues = []
        sunValuesHour = []

        print(statusMsg('Calculating sun positions and radiation values'))

        # We need to throw out all the warning values arising from times when sun isn't present.
        # os.devnull serves that purpose.
        with open(os.devnull,'w') as warningDump:
            for idx,timeStamp in enumerate(monthDateTime):
                month,day,hour = timeStamp.month,timeStamp.day,timeStamp.hour+0.5
                genParam.dirNormDifHorzIrrad = (epw.directNormalRadiation[idx],
                                                epw.diffuseHorizontalRadiation[idx])

                genDay.monthDayHour = (month,day,hour)
                genDay.gendaylitParameters = genParam
                gendayCmd = genDay.toRadString().split('|')[0]

                #run cmd, get results in the form of a list of lines.
                cmdRun = Popen(gendayCmd,stdout=PIPE,stderr=warningDump)
                data = cmdRun.stdout.read().split('\n')

                #clean the output by throwing out comments as well as brightness functions.
                sunCurrentValue = []
                for lines in data:
                    if not lines.strip().startswith("#"):
                        if "brightfunc" in lines:
                            break
                        if lines.strip():
                            sunCurrentValue.extend(lines.strip().split())

                #If a sun definition was captured in the last for-loop, store info.
                if sunCurrentValue and max(map(float, sunCurrentValue[6:9])):
                    sunCurrentValue[2] = 'solar%s' % (len(sunValues) + 1)
                    sunCurrentValue[9] = 'solar%s' % (len(sunValues) + 1)
                    sunValues.append(sunCurrentValue)
                    sunValuesHour.append(idx)

        numOfSuns = len(sunValues)

        print(statusMsg('Writing sun definitions to disc'))
        #create list of suns.
        with open(sunList,'w') as sunList:
            sunList.write("\n".join(["solar%s"%(idx+1) for idx in xrange(numOfSuns)]))

        #create solar discs.
        with open(sunDiscRadFile,'w') as solarDiscFile:
            solarDiscFile.write("\n".join([" ".join(sun) for sun in sunValues]))

        #Start creating header for the sun matrix.
        fileHeader = ['#?RADIANCE']
        fileHeader+= ['Sun matrix created by Honeybee']
        fileHeader+= ['LATLONG= %s %s'%(latitude,-longitude)]
        fileHeader+= ['NROWS=%s'%numOfSuns]
        fileHeader+= ['NCOLS=8760']
        fileHeader+= ['NCOMP=3']
        fileHeader+= ['FORMAT=ascii']

        #Write the matrix to file.
        with open(radiationMatrix,'w') as sunMtx:
            sunMtx.write("\n".join(fileHeader)+'\n'+'\n')
            for idx,sunValue in enumerate(sunValues):
                sunRadList = ["0 0 0"] * 8760
                sunRadList[sunValuesHour[idx]]=" ".join(sunValue[6:9])
                sunMtx.write("\n".join(sunRadList)+"\n"+"\n")

            #This last one is for the ground.
            sunRadList = ["0 0 0"] * 8760
            sunMtx.write("\n".join(sunRadList))

        print(statusMsg('Starting Raytrace calculations.'))

        octree = Oconv()
        octree.sceneFiles = sceneData+[r'tests/ASEtest/sunFile.rad']
        octree.outputFile = r'tests/ASEtest/roomSun.oct'
        octree.execute()

        rctPara = RcontribParameters()
        rctPara.ambientBounces=0
        rctPara.directJitter=0
        rctPara.directCertainty=1
        rctPara.directThreshold = 0
        rctPara.modFile=r'tests/ASEtest/sunlist'
        rctPara.irradianceCalc=True

        rctb = Rcontrib()
        rctb.octreeFile = r'tests/ASEtest/roomSun.oct'
        rctb.outputFile = r'tests/ASEtest/sunCoeff.dc'
        rctb.pointsFile =pointsFile
        rctb.rcontribParameters=rctPara

        rctb.execute()

        dct = Dctimestep()
        dct.daylightCoeffSpec = r'tests/ASEtest/sunCoeff.dc'
        dct.skyVectorFile = r'tests/ASEtest/sunRadiation.mtx'
        dct.outputFile = r'tests/ASEtest/illum.tmp'
        dct.execute()

        mtx2Param = RmtxopParameters()
        mtx2Param.outputFormat = 'a'
        mtx2Param.combineValues = (47.4, 119.9, 11.6)
        mtx2Param.transposeMatrix = True
        mtx2 = Rmtxop(matrixFiles=[r'tests/ASEtest/illum.tmp'], outputFile=annualResultsFile)
        mtx2.rmtxopParameters = mtx2Param
        mtx2.execute()

        print(statusMsg('Finished raytrace.'))

    # get points Data
    pointsList = []
    with open(pointsFile)as pointsData:
        for lines in pointsData:
            if lines.strip():
                pointsList.append(map(float, lines.strip().split()[:3]))

    hourlyIlluminanceValues = []
    with open(annualResultsFile) as resData:
        for lines in resData:
            lines = lines.strip()
            if lines:
                try:
                    tempIllData= map(float,lines.split())
                    hourlyIlluminanceValues.append(tempIllData)
                except ValueError:
                    pass
    if calcASE:
        #As per IES-LM-83-12 ASE is the percent of sensors in the analysis area that are
        # found to be exposed to more than 1000lux of direct sunlight for more than 250hrs
        # per year. The present script allows user to define what the lux and hour value
        # should be.
        sensorIllumValues = zip(*hourlyIlluminanceValues)
        aseData=[]
        for idx,sensor in enumerate(sensorIllumValues):
            x,y,z=pointsList[idx]
            countAboveThreshold = len([val for val in sensor if val>illumForASE])
            aseData.append([x,y,z,countAboveThreshold])

        sensorsWithHoursAboveLimit = [hourCount for x, y, z, hourCount in aseData if
                                      hourCount > hoursForASE]
        percentOfSensors = len(sensorsWithHoursAboveLimit) / len(pointsList) * 100
        print("ASE RESULT: Percent of sensors above %sLux for more than %s hours = %s%%"
              % (illumForASE, hoursForASE, percentOfSensors))

        if calcASEptsSummary:
            print("ASE RESULT: Location of sensors and # of hours above threshold of %sLux\n"%illumForASE)
            print("%12s %12s %12s %12s" % ('xCor', 'yCor', 'zCor', 'Hours'))
            for x,y,z,countAboveThreshold in aseData:
                print("%12.4f %12.4f %12.4f %12d" % (x, y, z, countAboveThreshold))


    #Stage 2: Check values from ASE calc against
    if hoyForValidation in xrange(8760):
        print(statusMsg('Starting validation calcs.'))



        #Create a sky for a point in time calc.
        timeStamp= monthDateTime[hoyForValidation]
        month, day, hour = timeStamp.month, timeStamp.day, timeStamp.hour + 0.5
        print("VALIDATION RESULTS: Comparing illuminancevalues for (month,day,hour):(%s, %s, %s)\n"%(month,day,hour))

        # msgString="\t\tComparing values for (month,day,hour):(%s, %s, %s)"%(month,day,hour)
        # print(msgString)
        # print("\t\t%s\n"%("~"*len(msgString)))

        genParam = GendaylitParameters()
        genParam.meridian=meridian
        genParam.longitude=longitude
        genParam.latitude=latitude

        genDay = Gendaylit()
        genParam.dirNormDifHorzIrrad = (epw.directNormalRadiation[hoyForValidation],
                                        epw.diffuseHorizontalRadiation[hoyForValidation])

        genDay.monthDayHour = (month,day,hour)
        genDay.gendaylitParameters = genParam
        genDay.outputFile = r'tests/ASEtest/genday.sky'
        genDay.execute()

        octGenday = Oconv()
        octGenday.sceneFiles = sceneData+[r'tests/ASEtest/genday.sky']
        octGenday.outputFile = r'tests/ASEtest/roomSunGenday.oct'
        octGenday.execute()

        rtcPara = GridBasedParameters()
        rtcPara.irradianceCalc = True
        rtcPara.ambientBounces=0
        rtcPara.directJitter=1
        rtcPara.directCertainty=1
        rtcPara.directThreshold=0

        rtc = Rtrace()
        rtc.radianceParameters = rtcPara
        rtc.octreeFile = r'tests/ASEtest/roomSunGenday.oct'
        rtc.pointsFile = pointsFile
        rtc.outputFile = r'tests/ASEtest/rtraceTest.res'
        rtc.execute()

        #This is a quick hack to get values out of rtrace. I think the option to turn of header is
        # nested inside.

        rtraceIllValues=[]
        with open(r'tests/ASEtest/rtraceTest.res') as resFile:
            for lines in resFile:
                lines = lines.strip()
                if lines:
                    try:
                        r,g,b = map(float,lines.strip().split())
                        r,g,b = r*47.4,g*119.9,b*11.6
                        rtraceIllValues.append(r+g+b)
                    except ValueError:
                        pass


        print("%12s %12s %12s %12s %12s %12s%%" %('xCor','yCor','zCor','Annual-Ill','Rtrace-Ill','Diff'))
        for point,aseVal,rtraceVal in zip(pointsList,hourlyIlluminanceValues[hoyForValidation],rtraceIllValues):
            x,y,z = point
            if rtraceVal:
                diff = (rtraceVal-aseVal)/rtraceVal
                aseVal,rtraceVal,diff = map(lambda x:round(x,4),(aseVal,rtraceVal,diff*100))
            else:
                aseVal, rtraceVal, diff = 0.0,0.0,0.0
                aseVal, rtraceVal, diff = map(lambda x: round(x, 4),
                                              (aseVal, rtraceVal, diff * 100))
            print("%12.4f %12.4f %12.4f %12.4f %12.4f %12.4f%%"%(x,y,z,aseVal,rtraceVal,diff))

    print(statusMsg('Done!'))

os.chdir(os.path.dirname(os.getcwd()))

epwFile = r'tests/assets/phoenix.epw'
materialFile = r'tests/assets/material.rad'
geometryFiles = r'tests/assets/geoSouth.rad'
pointsFile = r'tests/assets/2x2.pts'

directSunCalcs(epwFile, materialFile, geometryFiles, pointsFile,
                   calcASE=True, illumForASE=1000,
                hoursForASE=250, hoyForValidation=10,calcASEptsSummary=False,repeatValidationOnly=False)




