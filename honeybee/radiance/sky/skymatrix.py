from ladybug.wea import Wea
from ._skyBase import RadianceSky
from ..command.gendaymtx import Gendaymtx
from ..parameters.gendaymtx import GendaymtxParameters
import os


class SkyMatrix(RadianceSky):
    """Radiance sky matrix based on an epw weather file.

    Attributes:
        wea: An instance of ladybug Wea.
        skyDensity: A positive intger for sky density. [1] Tregenza Sky,
            [2] Reinhart Sky, etc. (Default: 1)
        north: An angle in degrees between 0-360 to indicate north direction
            (Default: 0).
        hoys: The list of hours for generating the sky matrix (Default: 0..8759).
        mode: Sky mode 0: total, 1: direct-only, 2: diffuse-only (Default: 0).
        suffix: An optional suffix for sky name. The suffix will be added at the
            end of the standard name. Use this input to customize the new and
            avoid sky being overwritten by other skymatrix components.
    """

    __slots__ = ('_wea', 'hoys', '_skyType', '_skyMatrixParameters',
                 '_mode', 'suffix', 'north')

    def __init__(self, wea, skyDensity=1, north=0, hoys=None, mode=0, suffix=None):
        """Create sky."""
        RadianceSky.__init__(self)
        self.wea = wea
        self.hoys = hoys or range(8760)
        skyDensity = skyDensity or 1
        self._skyType = 0  # default to visible radiation
        self._skyMatrixParameters = GendaymtxParameters(outputType=self._skyType)
        self.north = north
        self.skyDensity = skyDensity
        self.mode = mode
        self.suffix = suffix or ''

    @classmethod
    def fromEpwFile(cls, epwFile, skyDensity=1, north=0, hoys=None, mode=0, suffix=None):
        """Create sky from an epw file."""
        return cls(Wea.fromEpwFile(epwFile), skyDensity, north, hoys, mode,
                   suffix=suffix)

    @property
    def isSkyMatrix(self):
        """Return True."""
        return True

    @property
    def isClimateBased(self):
        """Return True if the sky is generated from values from weather file."""
        return True

    @property
    def skyMatrixParameters(self):
        """Return sky matrix parameters."""
        return self._skyMatrixParameters

    @property
    def wea(self):
        """An instance of ladybug Wea."""
        return self._wea

    @wea.setter
    def wea(self, w):
        assert hasattr(w, 'isWea'), \
            TypeError('wea must be a WEA object not a {}'.format(type(w)))
        self._wea = w

    @property
    def skyDensity(self):
        """A positive intger for sky density. [1] Tregenza Sky, [2] Reinhart Sky, etc."""
        return self._skyMatrixParameters.skyDensity

    @skyDensity.setter
    def skyDensity(self, s):
        skyDensity = s or 1
        self._skyMatrixParameters.skyDensity = skyDensity

    @property
    def north(self):
        """An angle in degrees between 0-360 to indicate north direction (Default: 0)."""
        return self._skyMatrixParameters.rotation

    @north.setter
    def north(self, n):
        north = n or 0
        self._skyMatrixParameters.rotation = north

    @property
    def mode(self):
        """Sky mode 0: total, 1: direct-only, 2: diffuse-only (Default: 0)."""
        return self._mode

    @mode.setter
    def mode(self, m):
        self._mode = m or 0
        if self._mode == 0:
            self._skyMatrixParameters.onlyDirect = False
            self._skyMatrixParameters.onlySky = False
        elif self._mode == 1:
            self._skyMatrixParameters.onlyDirect = True
            self._skyMatrixParameters.onlySky = False
        elif self._mode == 2:
            self._skyMatrixParameters.onlyDirect = False
            self._skyMatrixParameters.onlySky = True

    @property
    def name(self):
        """Sky default name."""
        return "skymtx_{}_r{}_{}_{}_{}_{}_{}{}".format(
            self.skyTypeHumanReadable, self.skyDensity,
            self.mode, self.wea.location.stationId,
            self.wea.location.latitude, self.wea.location.longitude, self.north,
            '_{}'.format(self.suffix) if self.suffix else ''
        )

    @property
    def skyType(self):
        """Specify 0 for visible radiation, 1 for total solar radiation."""
        return self._skyType

    @skyType.setter
    def skyType(self, t):
        """Specify 0 for visible radiation, 1 for total solar radiation."""
        self._skyType = t % 2
        self._skyMatrixParameters.outputType = self._skyType

    @property
    def skyTypeHumanReadable(self):
        """Human readable sky type."""
        values = ('vis', 'sol')
        return values[self.skyType]

    def hoursMatch(self, hoursFile):
        """Check if hours in the hours file matches the hours of wea."""
        if not os.path.isfile(hoursFile):
            return False

        with open(hoursFile, 'r') as hrf:
            line = hrf.read()
        return line == ','.join(str(h) for h in self.hoys) + '\n'

    def writeWea(self, targetDir, writeHours=False):
        """Write the wea file.

        WEA carries radiation values from epw and is what gendaymtx uses to
        generate the sky.
        Args:
            targetDir: Path to target directory.
            writeHours: Write hours in a separate file in folder.
        """
        weafilepath = os.path.join(targetDir, '{}.wea'.format(self.name))
        return self.wea.write(weafilepath, self.hoys, writeHours)

    def toRadString(self, workingDir, writeHours=False):
        """Get the radiance command line as a string."""
        # check if wea file in available otherwise include the line
        outfilepath = os.path.join(workingDir, '{}.smx'.format(self.name))
        weafilepath = os.path.join(workingDir, '{}.wea'.format(self.name))
        weafilepath = self.wea.write(weafilepath, self.hoys, writeHours)
        genday = Gendaymtx(weaFile=weafilepath, outputName=outfilepath)
        genday.gendaymtxParameters = self._skyMatrixParameters
        genday.gendaymtxParameters.outputType = self.skyType
        return genday.toRadString()

    def execute(self, workingDir, reuse=True):
        """Generate sky matrix.

        Args:
            workingDir: Folder to execute and write the output.
            reuse: Reuse the matrix if already existed in the folder.
        """
        outfilepath = os.path.join(workingDir, '{}.smx'.format(self.name))
        weafilepath = os.path.join(workingDir, '{}.wea'.format(self.name))
        hoursfilepath = weafilepath[:-4] + '.hrs'

        if reuse and os.path.isfile(outfilepath) and self.hoursMatch(hoursfilepath):
            print('Using the same SkyMatrix from an older run.'.format())
            return outfilepath
        else:
            outfilepath = os.path.join(workingDir, '{}.smx'.format(self.name))
            weafilepath = os.path.join(workingDir, '{}.wea'.format(self.name))
            weafilepath = self.wea.write(weafilepath)
            genday = Gendaymtx(weaFile=weafilepath, outputName=outfilepath)
            genday.gendaymtxParameters = self._skyMatrixParameters
            genday.gendaymtxParameters.outputType = self.skyType
            return genday.execute()

    def duplicate(self):
        """Duplicate this class."""
        skymtx = SkyMatrix(self.wea, self.skyDensity, self.north, self.hoys,
                           self.mode, self.suffix)
        skymtx.skyType = self.skyType
        return skymtx

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.name
