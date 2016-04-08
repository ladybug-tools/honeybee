# coding=utf-8
# coding=utf-8
from _commandbase import RadianceCommand
from ..datatype import RadiancePath,RadianceTuple
from ..parameters.gensky import GenSkyParameters

import os


class GenSky(RadianceCommand):
    u"""
    gensky - Generate an annual Perez sky matrix from a weather tape.

    The attributes for this class and their data descriptors are given below.
    Please note that the first two inputs for each descriptor are for internal
    naming purposes only.

    Attributes:
        monthDayHour: A tuple containing inputs for month,day and hour.
        outputName: An optional name for output file name. If None the name of
            .epw file will be used.
        genskyParameters: Radiance parameters for gensky. If None Default
            parameters will be set. You can use self.genskyParameters to view,
            add or remove the parameters before executing the command.

    Usage:

        from honeybee.radiance.parameters.gensky import GenSkyParameters
        from honeybee.radiance.command.gensky import GenSky

        # create and modify genskyParameters. In this case a sunny with no sun
        # will be generated.
        gnskyParam = GenSkyParameters()
        gnskyParam.sunnySkyNoSun = True

        # create the gensky Command.
        gnsky = GenSky(monthDayHour=(1,1,11),genskyParameters=gnskyParam,
        outputName = r'd:\sky.rad' )

        # run gensky
        gnsky.execute()

        >
    """
    monthDayHour = RadianceTuple('monthDayHour','month day hour',tupleSize=3,
                                 testType=False)

    outputName = RadiancePath('outputFile', descriptiveName='output sky file',
                              relativePath=None, checkExists=False)

    def __init__(self, monthDayHour=None, genskyParameters=None,outputName=None):
        """Init command."""
        RadianceCommand.__init__(self)
        self.monthDayHour = monthDayHour
        self.genskyParameters = genskyParameters
        self.outputName = outputName

    @property
    def monthDayHour(self):
        if self._monthDayHour:
            return " ".join(map(str,self._monthDayHour))
        else:
            return ''

    @monthDayHour.setter
    def monthDayHour(self,value):
        try:
            value = value.split()
        except AttributeError:
            pass

        assert len(value)==3,"The input for monthDayHour should be a tuple with" \
                             " three inputs for month day and hour."
        self._monthDayHour = value

    @property
    def genskyParameters(self):
        """Get and set genskyParameters."""
        return self.__genskyParameters

    @genskyParameters.setter
    def genskyParameters(self, genskyParam):
        self.__genskyParameters = genskyParam if genskyParam is not None \
            else GenSkyParameters()

        assert hasattr(self.genskyParameters, "isRadianceParameters"), \
            "input genskyParameters is not a valid parameters type."

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        # generate the name from self.weaFile
        outputFile = self.outputName
        monthDayHour = self.monthDayHour if self.monthDayHour else ''
        radString = "%s %s %s > %s" % (
            os.path.join(self.radbinPath, 'gensky'),
            self.monthDayHour,
            self.genskyParameters.toRadString(),
            outputFile
        )


        return radString

    @property
    def inputFiles(self):
        """Input files for this command."""
        return None