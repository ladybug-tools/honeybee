# coding=utf-8
from ._commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceTuple
from ..parameters.gendaylit import GendaylitParameters

import os


class Gendaylit(RadianceCommand):
    u"""
    gendaylit - Generate an annual Perez sky matrix from a weather tape.

    The attributes for this class and their data descriptors are given below.
    Please note that the first two inputs for each descriptor are for internal
    naming purposes only.

    Attributes:
        outputName: An optional name for output file name (Default: 'untitled').
        monthDayHour: A tuple containing inputs for month, day and hour.
        gendaylitParameters: Radiance parameters for gendaylit. If None Default
            parameters will be set. You can use self.gendaylitParameters to view,
            add or remove the parameters before executing the command.

    Usage:

        from honeybee.radiance.parameters.gendaylit import GendaylitParameters
        from honeybee.radiance.command.gendaylit import Gendaylit

        # create and modify gendaylit parameters.
        gndayParam = GendaylitParameters()
        gndayParam.dirNormDifHorzIrrad = (600,100)

        # create the gendaylit Command.
        gnday = Gendaylit(monthDayHour=(1,1,11), gendaylitParameters=gndayParam,
        outputName = r'd:/sunnyWSun_010111.sky' )

        # run gendaylit
        gnday.execute()

        >

    """

    monthDayHour = RadianceTuple('monthDayHour', 'month day hour', tupleSize=3,
                                 testType=False)

    outputFile = RadiancePath('outputFile', descriptiveName='output sky file',
                              relativePath=None, checkExists=False)

    def __init__(self, outputName, monthDayHour, rotation=0,
                 gendaylitParameters=None):
        """Init command."""
        RadianceCommand.__init__(self)

        outputName = outputName or 'untitled'
        self.outputFile = outputName if outputName.lower().endswith(".sky") \
            else outputName + ".sky"
        """results file for sky (Default: untitled)"""

        self.monthDayHour = monthDayHour
        self.rotation = rotation
        self.gendaylitParameters = gendaylitParameters

    @classmethod
    def fromLocationDirectAndDiffuseRadiation(
        cls, outputName, location, monthDayHour, directRadiation, diffuseRadiation,
            rotation=0):
        par = GendaylitParameters()
        par.latitude = location.latitude
        par.longitude = -location.longitude
        par.dirNormDifHorzIrrad = (directRadiation, diffuseRadiation)
        return cls(outputName, monthDayHour, rotation, par)

    @property
    def gendaylitParameters(self):
        """Get and set gendaylitParameters."""
        return self._gendaylitParameters

    @gendaylitParameters.setter
    def gendaylitParameters(self, gendaylitParam):
        self._gendaylitParameters = gendaylitParam if gendaylitParam is not None \
            else GendaylitParameters()

        assert hasattr(self.gendaylitParameters, "isRadianceParameters"), \
            "input gendaylitParameters is not a valid parameters type."

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        # generate the name from self.weaFile
        monthDayHour = self.monthDayHour.toRadString().replace("-monthDayHour ", "") if \
            self.monthDayHour else ''

        if self.rotation != 0:
            radString = "%s %s %s | xform -rz %.3f > %s" % (
                self.normspace(os.path.join(self.radbinPath, 'gendaylit')),
                monthDayHour,
                self.gendaylitParameters.toRadString(),
                self.rotation,
                self.normspace(self.outputFile.toRadString())
            )
        else:
            radString = "%s %s %s > %s" % (
                self.normspace(os.path.join(self.radbinPath, 'gendaylit')),
                monthDayHour,
                self.gendaylitParameters.toRadString(),
                self.normspace(self.outputFile.toRadString())
            )
        return radString

    @property
    def inputFiles(self):
        """Input files for this command."""
        return None
