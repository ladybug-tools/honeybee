# coding=utf-8

from ._commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceBoolFlag, RadianceValue
from ..parameters.genBsdf import GenbsdfParameters
from ..parameters.rtrace import RtraceParameters
from .getbbox import Getbbox
from .xform import Xform
import tempfile

import os
# TODO: 30thNov2016:


class GenBSDF(RadianceCommand):

    output_file = RadiancePath(
        'output_file',
        'output BSDF file in XML format',
        extension='.xml')
    normal_orientation = RadianceValue(
        'normal_orientation',
        'the orientation of the normal for the BSDF geometry',
        accepted_inputs=('+X', '+Y', '+Z', '-X', '-Y', '-Z',
                         '+x', '+y', '+z', '-x', '-y', '-z'))
    prepare_geometry = RadianceBoolFlag('prepare_geometry',
                                        'prepare geometry for BSDF')

    def __init__(self, input_geometry=None, gen_bsdf_parameters=None,
                 grid_based_parameters=None, output_file=None, normal_orientation=None,
                 prepare_geometry=True):
        RadianceCommand.__init__(self, executable_name='genBSDF.pl')

        self.grid_based_parameters = grid_based_parameters
        """The input for this attribute must be an instance of Grid based parameters"""

        self.gen_bsdf_parameters = gen_bsdf_parameters
        """These are parameters specific to genBsdf such as sampling, geometry dimensions
        etc."""

        self.input_geometry = input_geometry
        """Rad or mgf files that are inputs for genBSDF"""

        self.output_file = output_file
        """Path name for the XML file created by genBSDF"""

        self.normal_orientation = normal_orientation
        """Direction of the normal surface for the overall input geometry"""

        self.prepare_geometry = prepare_geometry
        """A boolean value to decide if the input geometry needs to be translated and
        rotated before being sent as input to genBSDf"""

    @property
    def input_geometry(self):
        """Get and set scene files."""
        return self.__input_geometry

    @input_geometry.setter
    def input_geometry(self, files):
        if files:
            self.__input_geometry = [os.path.normpath(f) for f in files]
        else:
            self.__input_geometry = None

    @property
    def gen_bsdf_parameters(self):
        """Get and set gen_bsdf_parameters."""
        return self.__gen_bsdf_parameters

    @gen_bsdf_parameters.setter
    def gen_bsdf_parameters(self, gen_bsdf_param):
        self.__gen_bsdf_parameters = gen_bsdf_param if gen_bsdf_param is not None \
            else GenbsdfParameters()

        assert hasattr(self.gen_bsdf_parameters, "isRadianceParameters"), \
            "input gen_bsdf_parameters is not a valid parameters type."

    @property
    def grid_based_parameters(self):
        return self.__grid_based_parameters

    @grid_based_parameters.setter
    def grid_based_parameters(self, grid_based_parameters):
        if grid_based_parameters:
            assert isinstance(grid_based_parameters, RtraceParameters),\
                'The input for rcontribOptions should be an instance of '\
                'Gridbased parameters'
            self.__grid_based_parameters = grid_based_parameters
        else:
            self.__grid_based_parameters = None

    def prepare_geometry_for_bsdf(self):
        """A method that will translate and rotate the model properly for genBSDF.
        """
        assert self.input_geometry,\
            'The files required for input_geometry have not been specified'

        assert self.normal_orientation._value, \
            'The input required for normal_orientation has not been specified'

        temp_for_getbox = tempfile.mktemp(prefix='getb')

        get_b = Getbbox()
        get_b.rad_files = self.input_geometry
        get_b.output_file = temp_for_getbox
        get_b.header_suppress = True
        get_b.execute()

        with open(temp_for_getbox) as get_box_data:
            get_box_value = get_box_data.read().strip().split()
            xMin, xMax, yMin, yMax, zMin, zMax = map(float, get_box_value)

        os.remove(temp_for_getbox)

        temp_for_xform = tempfile.mktemp(prefix='xform')

        xTr, yTr, zTr = 0 - xMin, 0 - yMin, 0 - zMin
        zTr += -0.001

        rotation_dict = {'+x': '-ry -90', '-x': '-ry 90',
                         '+y': '-rx 90', '-y': '-rx -90',
                         '+z': '', '-z': ''}
        rotation_normal = self.normal_orientation._value.lower()

        rot_tr = rotation_dict[rotation_normal]
        xfr = Xform()
        xfr.rad_file = [os.path.abspath(geo) for geo in self.input_geometry]
        xfr.transforms = "-t %s %s %s %s" % (xTr, yTr, zTr, rot_tr)
        xfr.output_file = temp_for_xform
        xfr.execute()

        return temp_for_xform

    def to_rad_string(self, relative_path=False):
        exe_name = 'genBSDF.pl' if os.name == 'nt' else 'genBSDF'
        cmd_path = self.normspace(os.path.join(self.radbin_path, exe_name))

        perl_path = self.normspace(self.perl_exe_path) if os.name == 'nt' else ''
        if os.name == 'nt':
            if not perl_path:
                raise IOError('Failed to find perl installation.\n'
                              'genBSDF.pl needs perl to run successfully.')
            else:
                cmd_path = "%s %s" % (perl_path, cmd_path)

        if self.grid_based_parameters:
            if os.name == 'nt':
                grid_based = '-r "%s"' % self.grid_based_parameters.to_rad_string()
            else:
                grid_based = "-r '%s'" % self.grid_based_parameters.to_rad_string()
        else:
            grid_based = ''

        if self.gen_bsdf_parameters:
            gen_bsdf_para = self.gen_bsdf_parameters.to_rad_string()
        else:
            gen_bsdf_para = ''

        if self.output_file and self.output_file._value:
            output_file = "> %s" % self.output_file.to_rad_string()
        else:
            output_file = ''

        file_path = " ".join(self.normspace(f) for f in self.input_geometry)

        command_string = "%s %s %s %s %s" % (cmd_path, gen_bsdf_para,
                                             grid_based, file_path, output_file)

        return command_string

    @property
    def input_files(self):
        return self.input_geometry

    def execute(self):
        if self.prepare_geometry._value:
            self.input_geometry = [self.prepare_geometry_for_bsdf()]

        RadianceCommand.execute(self)
