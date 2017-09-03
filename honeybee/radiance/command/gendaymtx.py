# coding=utf-8
from _commandbase import RadianceCommand
from ..parameters.gendaymtx import GendaymtxParameters

import os


class Gendaymtx(RadianceCommand):
    u"""
    gendaymtx - Generate an annual Perez sky matrix from a weather tape.

    Attributes:
        output_name: An optional name for output file name. If None the name of
            .epw file will be used.
        wea_file: Full path to input wea file (Default: None).
        gendaymtx_parameters: Radiance parameters for gendaymtx. If None Default
            parameters will be set. You can use self.gendaymtx_parameters to view,
            add or remove the parameters before executing the command.

    Usage:

        from honeybee.radiance.parameters.gendaymtx import GendaymtxParameters
        from honeybee.radiance.command.gendaymtx import Gendaymtx

        # create and modify gendaymtx_parameters
        # generate sky matrix with default values
        gmtx = GendaymtxParameters()

        # ask only for direct sun
        gmtx.only_direct = True

        # create gendaymtx
        dmtx = Gendaymtx(wea_file="C:/IZMIR_TUR.wea", gendaymtx_parameters=gmtx)

        # run gendaymtx
        dmtx.execute()
        > c:/radiance/bin/gendaymtx: reading weather tape 'C:/ladybug/IZMIR_TUR.wea'
        > c:/radiance/bin/gendaymtx: location 'IZMIR_TUR'
        > c:/radiance/bin/gendaymtx: (lat,long)=(38.5,-27.0) degrees north, west
        > c:/radiance/bin/gendaymtx: 146 sky patches per time step
        > c:/radiance/bin/gendaymtx: stepping through month 1...
        > c:/radiance/bin/gendaymtx: stepping through month 2...
        > c:/radiance/bin/gendaymtx: stepping through month 3...
        > c:/radiance/bin/gendaymtx: stepping through month 4...
        > c:/radiance/bin/gendaymtx: stepping through month 5...
        > c:/radiance/bin/gendaymtx: stepping through month 6...
        > c:/radiance/bin/gendaymtx: stepping through month 7...
        > c:/radiance/bin/gendaymtx: stepping through month 8...
        > c:/radiance/bin/gendaymtx: stepping through month 9...
        > c:/radiance/bin/gendaymtx: stepping through month 10...
        > c:/radiance/bin/gendaymtx: stepping through month 11...
        > c:/radiance/bin/gendaymtx: stepping through month 12...
        > c:/radiance/bin/gendaymtx: writing matrix with 8760 time steps...
        > c:/radiance/bin/gendaymtx: done.

        # change it not to be verbose
        dmtx.gendaymtx_parameters.verbose_report = False

        # run it again
        dmtx.execute()
        >
    """

    def __init__(self, output_name=None, wea_file=None, gendaymtx_parameters=None):
        """Init command."""
        RadianceCommand.__init__(self)

        self.output_name = output_name
        self.wea_file = wea_file
        self.gendaymtx_parameters = gendaymtx_parameters

    @property
    def gendaymtx_parameters(self):
        """Get and set gendaymtx_parameters."""
        return self.__gendaymtx_parameters

    @gendaymtx_parameters.setter
    def gendaymtx_parameters(self, mtx):
        self.__gendaymtx_parameters = mtx if mtx is not None \
            else GendaymtxParameters()

        assert hasattr(self.gendaymtx_parameters, "isRadianceParameters"), \
            "input gendaymtx_parameters is not a valid parameters type."

    @property
    def output_file(self):
        """Output file address."""
        return os.path.splitext(str(self.wea_file))[0] + ".mtx" \
            if self.output_name is None and self.wea_file.normpath is not None \
            else self.output_name

    def to_rad_string(self, relative_path=False):
        """Return full command as a string."""
        # generate the name from self.wea_file
        rad_string = "%s %s %s > %s" % (
            self.normspace(os.path.join(self.radbin_path, 'gendaymtx')),
            self.gendaymtx_parameters.to_rad_string(),
            self.normspace(self.wea_file),
            self.normspace(self.output_file)
        )

        # make sure input files are set by user
        self.check_input_files(rad_string)
        return rad_string

    @property
    def input_files(self):
        """Input files for this command."""
        return self.wea_file,
