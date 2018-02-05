# coding=utf-8
from ._commandbase import RadianceCommand
from ..datatype import RadianceBoolFlag, RadianceValue
from ..datatype import RadianceNumber
import os

from .pyRad import objview


class Objview(RadianceCommand):
    use_open_gl = RadianceBoolFlag('g', 'use GlRad(openGl) to render the scene')
    hemisphere_up = RadianceValue('u', 'hemisphere up direction')
    back_face_visibility = RadianceBoolFlag('bv', 'back face visibility')
    view_details = RadianceValue('v', 'view details')
    num_processors = RadianceNumber('N',
                                    'number of processors to render the scene',
                                    num_type=int)
    output_device = RadianceValue('o', 'output device to be used for rendering')
    verbose_display = RadianceBoolFlag('e', 'display errors and messages')
    disable_warnings = RadianceBoolFlag('w', 'disable warnings')
    gl_rad_full_screen = RadianceBoolFlag('S',
                                          'enable full screen options with glRad')
    view_file = RadianceValue('vf', 'view file path')
    scene_exposure = RadianceNumber('exp', 'scene exposure', num_type=float)
    no_lights = RadianceBoolFlag('nL', 'render the scene without extra lights')
    run_silently = RadianceBoolFlag('s', 'run the Radiance scene silently')
    print_views = RadianceBoolFlag('V', 'print view details to standard output')

    def __init__(self, use_open_gl=None, hemisphere_up=None, back_face_visibility=None,
                 view_details=None, num_processors=None, output_device=None,
                 verbose_display=None, disable_warnings=None, gl_rad_full_screen=None,
                 view_file=None, scene_exposure=None, no_lights=None,
                 run_silently=None, print_views=None, scene_files=None):

        RadianceCommand.__init__(self, executable_name='objview.pl')

        self.use_open_gl = use_open_gl
        self.hemisphere_up = hemisphere_up
        self.back_face_visibility = back_face_visibility
        self.view_details = view_details
        self.num_processors = num_processors
        self.output_device = output_device
        self.verbose_display = verbose_display
        self.disable_warnings = disable_warnings
        self.gl_rad_full_screen = gl_rad_full_screen
        self.view_file = view_file
        self.scene_exposure = scene_exposure
        self.no_lights = no_lights
        self.run_silently = run_silently
        self.print_views = print_views
        self.scene_files = scene_files

    @property
    def scene_files(self):
        """Get and set scene files."""
        return self.__scene_files

    @scene_files.setter
    def scene_files(self, files):
        if files:
            self.__scene_files = [os.path.normpath(f) for f in files]
        else:
            self.__scene_files = []

    def to_rad_string(self, relative_path=False):
        objview_python_path = objview.__file__
        cmd_path = self.normspace(objview_python_path)

        use_open_gl = self.use_open_gl.to_rad_string()
        hemisphere_up = self.hemisphere_up.to_rad_string()
        back_face_visibility = self.back_face_visibility.to_rad_string()
        view_details = self.view_details.to_rad_string()
        num_processors = self.num_processors.to_rad_string()
        output_device = self.output_device.to_rad_string()
        verbose_display = self.verbose_display.to_rad_string()
        disable_warnings = self.disable_warnings.to_rad_string()
        gl_rad_full_screen = self.gl_rad_full_screen.to_rad_string()
        view_file = self.view_file.to_rad_string()
        scene_exposure = self.scene_exposure.to_rad_string()
        no_lights = self.no_lights.to_rad_string()
        run_silently = self.run_silently.to_rad_string()
        print_views = self.print_views.to_rad_string()

        rad_string = "%s %s " % (self.python_exe_path, cmd_path)

        # Lambda shortcut for adding an input or nothing to the command
        def add_to_str(val):
            return "%s " % val if val else ''
        objview_param = (use_open_gl, hemisphere_up, back_face_visibility, view_details,
                         num_processors, output_device, verbose_display,
                         disable_warnings, gl_rad_full_screen, view_file, scene_exposure,
                         no_lights, run_silently, print_views)

        for parameter in objview_param:
            rad_string += add_to_str(parameter)

        rad_string += " %s" % (" ".join(self.scene_files))

        # make sure input files are set by user
        self.check_input_files(rad_string)

        return rad_string

    @property
    def input_files(self):
        """Return input files by user."""
        return self.scene_files
