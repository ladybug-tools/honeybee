from ladybug.wea import Wea
from ..command.gendaylit import Gendaylit, GendaylitParameters
from ladybug.wea import Wea
from ladybug.dt import DateTime
from subprocess import PIPE, Popen

import os
import tempfile


# TODO: Add checks for input files
class SunMatrix(object):
    """Radiance sun matrix created from epw file.

    Attributes:
        wea: An instance of ladybug Wea.
        skyDensity: A positive intger for sky density. [1] Tregenza Sky,
            [2] Reinhart Sky, etc. (Default: 1)
        north: An angle in degrees between 0-360 to indicate north direction
            (Default: 0).
        hoys: The list of hours for generating the sky matrix (Default: 0..8759)
    """

    def __init__(self, wea, destinationDirectory=None, useExisting=True):

        assert hasattr(wea, 'isWea'), '{} is not an instance of Wea.'.format(wea)
        self.wea = wea

        if destinationDirectory and os.path.exists(destinationDirectory):
            sunMatrixFile = os.path.join(destinationDirectory, 'sunMatrix.mtx')
            sunRadFile = os.path.join(destinationDirectory, 'sunRadFile.rad')
            sunlist = os.path.join(destinationDirectory, 'sunList.txt')
        else:
            sunMatrixFile = tempfile.mktemp(suffix='sunMatrix.mtx')
            sunRadFile = tempfile.mktemp(suffix='sunRadFile.rad')
            sunlist = tempfile.mktemp(suffix='sunList.txt')

        if useExisting:
            for fileName in sunMatrixFile, sunRadFile, sunlist:
                assert os.path.exists(fileName), \
                    'The files required for reuse do not exist.'

        self.sunMatrixFile = sunMatrixFile
        self.sunRadFile = sunRadFile
        self.sunList = sunlist

    @property
    def wea(self):
        return self._wea

    @wea.setter
    def wea(self, weaObject):
        assert hasattr(weaObject, 'isWea'), \
            '{} is not an instance of Wea.'.format(weaObject)
        self._wea = weaObject

    @property
    def isSunMatrix(self):
        """Return True."""
        return True

    @property
    def name(self):
        """Sky default name."""
        return "SUNMTX_r{}_{}_{}_{}".format(
            self.wea.location.stationId,
            self.wea.location.city.replace(' ', ''),
            self.wea.location.latitude,
            self.wea.location.longitude
        )

    def execute(self):
        """Generate sky matrix.

        Args:
            workingDir: Folder to execute and write the output.
            reuse: Reuse the matrix if already existed in the folder.
        """
        monthDateTime = [DateTime.fromHoy(idx) for idx in xrange(8760)]

        latitude, longitude = self.wea.location.latitude, -self.wea.location.longitude
        meridian = -(15 * self.wea.location.timezone)

        genParam = GendaylitParameters()
        genParam.meridian = meridian
        genParam.longitude = longitude
        genParam.latitude = latitude

        genDay = Gendaylit()

        sunValues = []
        sunValuesHour = []

        with open(os.devnull, 'w') as warningDump:
            for idx, timeStamp in enumerate(monthDateTime):
                month, day, hour = timeStamp.month, timeStamp.day, timeStamp.hour + 0.5
                genParam.dirNormDifHorzIrrad = (self.wea.directNormalRadiation[idx],
                                                self.wea.diffuseHorizontalRadiation[idx])

                genDay.monthDayHour = (month, day, hour)
                genDay.gendaylitParameters = genParam
                gendayCmd = genDay.toRadString().split('|')[0]

                # run cmd, get results in the form of a list of lines.
                cmdRun = Popen(gendayCmd.split(), stdout=PIPE, stderr=warningDump,
                               shell=True)
                data = cmdRun.stdout.read().split('\n')

                # clean the output by throwing out comments as well as brightness
                # functions.
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
                    sunValuesHour.append(idx)

        numOfSuns = len(sunValues)

        with open(self.sunList, 'w') as sunList:
            sunList.write("\n".join(["solar%s" % (idx + 1)
                                     for idx in xrange(numOfSuns)]))

        # create solar discs.
        with open(self.sunRadFile, 'w') as solarDiscFile:
            solarDiscFile.write("\n".join([" ".join(sun) for sun in sunValues]))

        # Start creating header for the sun matrix.
        fileHeader = ['#?RADIANCE']
        fileHeader += ['Sun matrix created by Honeybee']
        fileHeader += ['LATLONG= %s %s' % (latitude, -longitude)]
        fileHeader += ['NROWS=%s' % numOfSuns]
        fileHeader += ['NCOLS=8760']
        fileHeader += ['NCOMP=3']
        fileHeader += ['FORMAT=ascii']

        # Write the matrix to file.
        with open(self.sunMatrixFile, 'w') as sunMtx:
            sunMtx.write("\n".join(fileHeader) + '\n' + '\n')
            for idx, sunValue in enumerate(sunValues):
                sunRadList = ["0 0 0"] * 8760
                sunRadList[sunValuesHour[idx]] = " ".join(sunValue[6:9])
                sunMtx.write("\n".join(sunRadList) + "\n" + "\n")

            # This last one is for the ground.
            sunRadList = ["0 0 0"] * 8760
            sunMtx.write("\n".join(sunRadList))

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.name
