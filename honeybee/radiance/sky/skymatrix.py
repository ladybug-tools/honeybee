from ladybug.wea import Wea
from ._skyBase import RadianceSky
from ..command.gendaymtx import Gendaymtx
import os


# TODO: Add checks for input files
class SkyMatrix(RadianceSky):
    """Radiance sky matrix based on an epw weather file.

    Attributes:
        wea: An instance of ladybug Wea.
        skyDensity: A positive intger for sky density. [1] Tregenza Sky,
            [2] Reinhart Sky, etc. (Default: 1)
        north: An angle in degrees between 0-360 to indicate north direction
            (Default: 0).
        hoys: The list of hours for generating the sky matrix (Default: 0..8759)
    """

    def __init__(self, wea, skyDensity, north=0, hoys=None):
        """Create sky."""
        RadianceSky.__init__(self)
        assert hasattr(wea, 'isWea'), '{} is not an instance of Wea.'.format(wea)
        self.wea = wea
        self.skyDensity = skyDensity or 1
        self.hoys = hoys or range(8760)
        self.north = float(north)

    @classmethod
    def fromEpwFile(cls, epwFile, skyDensity=1, north=0):
        """Create sky from an epw file."""
        return cls(Wea.fromEpwFile(epwFile), skyDensity, north)

    @property
    def isSkyMatrix(self):
        """Return True."""
        return True

    @property
    def isClimateBased(self):
        """Return True if the sky is generated from values from weather file."""
        return True

    @property
    def name(self):
        """Sky default name."""
        return "SKYMTX_r{}_{}_{}_{}_{}_{}".format(
            self.skyDensity, self.wea.location.stationId,
            self.wea.location.city.replace(' ', ''),
            self.wea.location.latitude,
            self.wea.location.longitude,
            self.north
        )

    @property
    def main(self):
        """Generate Radiance's line for sky with certain illuminance value."""
        return ''

    def hoursMatch(self, hoursFile):
        """Check if hours in the hours file matches the hours of wea."""
        print 'Checking available sky matrix in folder...'
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
        genday.gendaymtxParameters.skyDensity = self.skyDensity
        genday.gendaymtxParameters.rotation = self.north
        return genday.toRadString()

    def execute(self, workingDir, reuse=True):
        """Generate sky matrix.

        Args:
            workingDir: Folder to execute and write the output.
            reuse: Reuse the matrix if already existed in the folder.
        """
        outfilepath = os.path.join(workingDir, '{}.smx'.format(self.name))
        weafilepath = os.path.join(workingDir, '{}.wea'.format(self.name))
        if reuse and os.path.isfile(outfilepath):
            return outfilepath
        else:
            outfilepath = os.path.join(workingDir, '{}.smx'.format(self.name))
            weafilepath = os.path.join(workingDir, '{}.wea'.format(self.name))
            weafilepath = self.wea.write(weafilepath)
            genday = Gendaymtx(weaFile=weafilepath, outputName=outfilepath)
            genday.gendaymtxParameters.skyDensity = self.skyDensity
            genday.gendaymtxParameters.rotation = self.north
            return genday.execute()

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.name
