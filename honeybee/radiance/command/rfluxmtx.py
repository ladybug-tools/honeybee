# coding=utf-8

from ._commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceValue, RadianceNumber
from ..datatype import RadianceBoolFlag
from ..parameters.rfluxmtx import RfluxmtxParameters

import os


# TODO (sarith and mostapha): move parameters such as output_data_format to command
# parameters. They are not command inputs.
class Rfluxmtx(RadianceCommand):
    """Radiance Rfluxmtx matrix."""

    ground_string = """
    void glow ground_glow
    0
    0
    4 1 1 1 0

    ground_glow source ground
    0
    0
    4 0 0 -1 180
    """

    sky_string = """
    void glow sky_glow
    0
    0
    4 1 1 1 0

    sky_glow source sky
    0
    0
    4 0 0 1 180
    """

    @staticmethod
    def control_parameters(hemi_type='u', hemi_up_direction='Y', output_file=''):
        """Rfluxmtx ControlParameters."""
        return RfluxmtxControlParameters(hemi_type, hemi_up_direction, output_file)

    @staticmethod
    def default_sky_ground(file_name, sky_type=None, sky_file_format=None,
                           ground_file_format=None):
        """

        Args:
            file_name:This should be the name of the file to which the sky defintion
                should be written to.

            sky_type:The acceptable inputs for hemisphere type are:
                    u for uniform.(Usually applicable for ground).\n
                    kf for klems full.\n
                    kh for klems half.\n
                    kq for klems quarter.\n
                    rN for Reinhart - Tregenza type skies. N stands for
                        subdivisions and defaults to 1.\n
                    scN for shirley-chiu subdivisions.

        Returns:
            file_name: Passes back the same file_name that was provided as input.
        """

        sky_param = Rfluxmtx.control_parameters(hemi_type=sky_type or 'r',
                                                output_file=sky_file_format)

        ground_param = Rfluxmtx.control_parameters(hemi_type='u',
                                                   output_file=ground_file_format)

        ground_string = Rfluxmtx.add_control_parameters(Rfluxmtx.ground_string,
                                                        {'ground_glow': ground_param})
        sky_string = Rfluxmtx.add_control_parameters(Rfluxmtx.sky_string,
                                                     {'sky_glow': sky_param})

        with open(file_name, 'w')as skyFile:
            skyFile.write(ground_string + '\n' + sky_string)

        return file_name

    @staticmethod
    def add_control_parameters(input_string, modifier_dict):
        if os.path.exists(input_string):
            with open(input_string)as fileString:
                file_data = fileString.read()
        else:
            file_data = input_string

        output_string = ''
        check_dict = dict.fromkeys(modifier_dict.keys(), None)
        for lines in file_data.split('\n'):
            for key, value in modifier_dict.items():
                if key in lines and not check_dict[key] and \
                        not lines.strip().startswith('#'):
                    output_string += str(value) + '\n'
                    check_dict[key] = True
            else:
                output_string += lines.strip() + '\n'

        for key, value in check_dict.items():
            assert value, "The modifier %s was not found in the string specified" % key

        if os.path.exists(input_string):
            new_output_file = input_string[:-4] + '_cp_added' + input_string[-4:]
            with open(new_output_file, 'w') as newoutput:
                newoutput.write(output_string)
            output_string = new_output_file

        return output_string

    @staticmethod
    def check_for_rflux_parameters(file_val):
        with open(file_val)as rfluxFile:
            rflux_string = rfluxFile.read()
        assert '#@rfluxmtx' in rflux_string, \
            "The file %s does not have any rfluxmtx control parameters."
        return True

    # sender = RadiancePath('sender','sender file')
    receiver_file = RadiancePath('receiver', 'receiver file')
    octree_file = RadiancePath('octree', 'octree file', extension='.oct')
    output_matrix = RadiancePath('output_matrix', 'output Matrix File')
    view_rays_file = RadiancePath('view_rays_file',
                                  'file containing ray samples generated by vwrays')
    output_data_format = RadianceValue('f', 'output data format', is_joined=True)
    verbose = RadianceBoolFlag('v', 'verbose commands in stdout')
    num_processors = RadianceNumber('n', 'number of processors', num_type=int)

    # TODO: This method misses RfluxmtxParameters as an input.
    def __init__(self, sender=None, receiver_file=None, octree_file=None,
                 rad_files=None, points_file=None, output_matrix=None,
                 view_rays_file=None, view_info_file=None, output_filename_format=None,
                 num_processors=None):

        RadianceCommand.__init__(self)

        self.sender = sender
        """Sender file will be either a rad file containing rfluxmtx variables
         or just a - """

        self.receiver_file = receiver_file
        """Receiver file will usually be the sky file containing rfluxmtx
        variables"""

        self.octree_file = octree_file
        """Octree file containing the other rad file in the scene."""

        self.rad_files = rad_files
        """Rad files other than the sender and receiver that are a part of the
          scene."""

        self.points_file = points_file
        """The points file or input vwrays for which the illuminance/luminance
        value are to be calculated."""

        self.number_of_points = 0
        """Number of test points. Initially set to 0."""

        self.output_matrix = output_matrix
        """The flux matrix file that will be created by rfluxmtx."""

        self.view_rays_file = view_rays_file
        """File containing ray samples generated from vwrays"""

        self.view_info_file = view_info_file
        """File containing view dimensions calculated from vwrays."""

        self.output_filename_format = output_filename_format
        """Filename format"""

        self.num_processors = num_processors
        """Number of processors"""

    @property
    def output_filename_format(self):
        return self._output_filename_format

    @output_filename_format.setter
    def output_filename_format(self, value=None):
        # TODO: Add testing logic for this !
        self._output_filename_format = value

    @property
    def view_info_file(self):
        return self._view_info_file

    @view_info_file.setter
    def view_info_file(self, file_name):
        """
            The input for this setter is a file containing the view dimensions
            calculated through the -d option in rfluxmtx.
        """
        if file_name:
            assert os.path.exists(file_name),\
                "The file %s specified as view_info_file does not exist." % file_name
            self._view_info_file = file_name
            with open(file_name) as view_fileName:
                self._view_fileDimensions = view_fileName.read().strip()
        else:
            self._view_info_file = ''
            self._view_fileDimensions = ''

    @property
    def points_file(self):
        return self._points_file

    @points_file.setter
    def points_file(self, value):
        if value:
            if os.path.exists(value):
                with open(value, 'rb') as pfile:
                    self.number_of_points = sum(1 for line in pfile if line.strip())
            elif self.number_of_points == 0:
                print('Warning: Failed to find the points_file at "{}".'
                      ' Use number_of_points method to set the number_of_points'
                      'separately.')

            self._points_file = value
        else:
            self._points_file = ''

    @property
    def rad_files(self):
        """Get and set scene files."""
        return self.__rad_files

    @rad_files.setter
    def rad_files(self, files):
        if files:
            self.__rad_files = [os.path.normpath(f) for f in files]
        else:
            self.__rad_files = []

    @property
    def rfluxmtx_parameters(self):
        return self.__rfluxmtx_parameters

    @rfluxmtx_parameters.setter
    def rfluxmtx_parameters(self, parameters):
        self.__rfluxmtx_parameters = parameters or RfluxmtxParameters()

        assert hasattr(self.rfluxmtx_parameters, "isRfluxmtxParameters"), \
            "input rfluxmtx_parameters is not a valid parameters type."

    def to_rad_string(self, relative_path=False):
        octree = self.octree_file.to_rad_string()
        octree = '-i %s' % self.normspace(octree) if octree else ''
        output_data_format = self.output_data_format.to_rad_string()
        verbose = self.verbose.to_rad_string()

        number_of_processors = self.num_processors.to_rad_string()
        number_of_points = '-y %s' % self.number_of_points \
            if self.number_of_points > 0 else ''
        points_file = self.normspace(self.points_file)
        points_file = '< %s' % points_file if points_file else ''

        view_file_samples = self.normspace(self.view_rays_file.to_rad_string())
        view_file_samples = '< %s' % view_file_samples if view_file_samples else ''

        assert not (points_file and view_file_samples),\
            'View file and points file cannot be specified at the same time!'

        input_rays = points_file or view_file_samples

        output_matrix = self.normspace(self.output_matrix.to_rad_string())
        output_matrix = "> %s" % output_matrix if output_matrix else ''

        output_filename_format = self.output_filename_format
        output_filename_format = "-o %s" % output_filename_format if \
            output_filename_format else ''

        # method for adding an input or nothing to the command
        def add_to_str(val):
            return "%s " % val if val else ''

        # Creating the string this way because it might change again in the
        # future.
        rad_string = ["%s " % self.normspace(os.path.join(self.radbin_path, 'rfluxmtx'))]
        rad_string.append(add_to_str(output_data_format))
        rad_string.append(add_to_str(verbose))
        rad_string.append(add_to_str(number_of_processors))
        rad_string.append(add_to_str(number_of_points))
        rad_string.append(add_to_str(self._view_fileDimensions))
        if str(self.sender).strip() == '-':
            rad_string.append(add_to_str(self.rfluxmtx_parameters.to_rad_string()))
        else:
            # -I and -i options are only valid for pass-through cases
            rflux_par = add_to_str(
                self.rfluxmtx_parameters.to_rad_string()).replace(
                '-I', '')
            rad_string.append(rflux_par)
        rad_string.append(add_to_str(output_filename_format))
        rad_string.append(add_to_str(self.sender))
        rad_string.append(add_to_str(self.normspace(self.receiver_file.to_rad_string())))
        rad_string.append(add_to_str(" ".join(self.rad_files)))
        rad_string.append(add_to_str(octree))
        rad_string.append(add_to_str(input_rays))
        rad_string.append(add_to_str(output_matrix))

        return ''.join(rad_string)

    @property
    def input_files(self):
        return [self.receiver_file] + self.rad_files


class RfluxmtxControlParameters(object):
    """Rfluxmtx ControlParameters.

    Set the values for hemispheretype, hemisphere up direction and output file
    location (optional).
    """

    def __init__(self, hemi_type='u', hemi_up_direction='Y', output_file=''):
        """Init class."""
        self.hemisphere_type = hemi_type
        """
            The acceptable inputs for hemisphere type are:
                u for uniform.(Usually applicable for ground).
                kf for klems full.
                kh for klems half.
                kq for klems quarter.
                rN for Reinhart - Tregenza type skies. N stands for subdivisions
                    and defaults to 1.
                scN for shirley-chiu subdivisions."""
        self.hemisphere_up_direction = hemi_up_direction
        """The acceptable inputs for hemisphere direction are %s""" % \
            (",".join(('X', 'Y', 'Z', 'x', 'y', 'z', '-X', '-Y',
                       '-Z', '-x', '-y', '-z')))
        self.output_file = output_file

    @property
    def hemisphere_type(self):
        return self._hemisphereType

    @hemisphere_type.setter
    def hemisphere_type(self, value):
        """Hemisphere type.

        The acceptable inputs for hemisphere type are:
            u for uniform.(Usually applicable for ground).
            kf for klems full.
            kh for klems half.
            kq for klems quarter.
            rN for Reinhart - Tregenza type skies. N stands for subdivisions and
                defaults to 1.
            scN for shirley-chiu subdivisions.
        """
        if value:
            if value in ('u', 'kf', 'kh', 'kq'):
                self._hemisphereType = value
                return
            elif value.startswith('r'):
                if len(value) > 1:
                    try:
                        num = int(value[1:])
                    except ValueError:
                        raise Exception(
                            "The format reinhart tregenza type skies is rN ."
                            "The value entered was %s" % value)
                else:
                    num = ''
                self._hemisphereType = 'r' + str(num)
            elif value.startswith('sc'):
                if len(value) > 2:
                    try:
                        num = int(value[2:])
                    except ValueError:
                        raise Exception(
                            "The format for ShirleyChiu type values is scN."
                            "The value entered was %s" % value)
                else:
                    raise Exception(
                        "The format for ShirleyChiu type values is scN."
                        "The value entered was %s" % value)
                self._hemisphereType = 'sc' + str(num)
            else:
                except_str = """
                The acceptable inputs for hemisphere type are:
                    u for uniform.(Usually applicable for ground).
                    kf for klems full.
                    kh for klems half.
                    kq for klems quarter.
                    rN for Reinhart - Tregenza type skies. N stands for
                        subdivisions and defaults to 1.
                    scN for shirley-chiu subdivisions.
                The value entered was %s
                """ % (value)
                raise Exception(except_str)

    @property
    def hemisphere_up_direction(self):
        return self._hemisphere_upDirection

    @hemisphere_up_direction.setter
    def hemisphere_up_direction(self, value):
        """hemisphere direction.

        The acceptable inputs for hemisphere direction are a tuple with 3 values
        or 'X', 'Y', 'Z', 'x', 'y', 'z', '-X', '-Y','-Z', '-x', '-y','-z'.
        """
        allowed_values = ('X', 'Y', 'Z', 'x', 'y', 'z', '-X', '-Y',
                          '-Z', '-x', '-y', '-z', "+X", "+Y", "+Z",
                          '+x', "+y", "+z")

        if isinstance(value, (tuple, list)):
            assert len(value) == 3, \
                'Length of emisphereUpDirection vector should be 3.'
            self._hemisphere_upDirection = ','.join((str(v) for v in value))

        elif value:
            assert value in allowed_values, "The value for hemisphere_upDirection" \
                "should be one of the following: %s" \
                % (','.join(allowed_values))

            self._hemisphere_upDirection = value
        else:
            self._hemisphere_upDirection = '+Z'

    def __str__(self):
        output_file_spec = "o=%s" % self.output_file if self.output_file else ''
        return "#@rfluxmtx h=%s u=%s %s" % (self.hemisphere_type,
                                            self.hemisphere_up_direction,
                                            output_file_spec)
