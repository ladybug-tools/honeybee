from ladybug.epw import EPW
from ._skyBase import RadianceSky
from ..command.gendaymtx import Gendaymtx
import os


# TODO: Add analysis period to sky matrix.
class SkyMatrix(RadianceSky):
    """Radiance sky matrix based on an epw weather file.

    Attributes:
        epwFile: Full filepath to a weather file.
        skyDensity: A positive intger for sky density. [1] Tregenza Sky,
            [2] Reinhart Sky, etc. (Default: 1)
        north: An angle between 0-360 to indicate north direction (Default: 0).
        hoys: The list of hours for generating the sky matrix (Default: 0..8759)
    """

    def __init__(self, epwFile, skyDensity=1, north=0, hoys=None):
        """Create sky."""
        RadianceSky.__init__(self)
        assert os.path.isfile(epwFile), 'Invalid path: {}'.format(epwFile)
        assert epwFile.lower().endswith('.epw'), 'Invalid epw file: {}'.format(epwFile)
        self.epwFile = os.path.normpath(epwFile)
        self.epwData = EPW(self.epwFile)
        self.skyDensity = skyDensity or 1
        self.north = north
        self.hoys = range(8760)

    @property
    def isClimateBased(self):
        """Return True if the sky is generated from values from weather file."""
        return True

    @property
    def name(self):
        """Sky default name."""
        return "SKYMTX_r{}_{}_{}_{}_{}".format(
            self.skyDensity, self.epwData.location.stationId,
            self.epwData.location.city.replace(' ', ''),
            self.epwData.location.latitude,
            self.epwData.location.longitude
        )

    @property
    def main(self):
        """Generate Radiance's line for sky with certain illuminance value."""
        return " "

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

        weafilepath = self.epwData.epw2wea(weafilepath)
        genday = Gendaymtx(weaFile=weafilepath, outputName=outfilepath)
        genday.gendaymtxParameters.skyDensity = self.skyDensity
        genday.execute()
        return outfilepath

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.name
