#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    objview - view RADIANCE object(s)

    This script is essentially a re-write of Axel Jacobs' objview.pl from
    http://radiance-online.org/cgi-bin/viewcvs.cgi/ray/src/util/objview.pl

    Axel's script inturn is a re-write of Greg Ward's original c-shell script.

    Sarith Subramaniam <sarith@sarith.in>,2016.
"""

from __future__ import division, print_function, unicode_literals
import os
import sys
import argparse
import tempfile
import shutil

__all__ = ('main')

# if __name__ == '__main__' and not getattr(sys, 'frozen', False):
#     _rp = os.environ.get('RAYPATH')
#     if not _rp:
#         print('No RAYPATH, unable to find support library');
#         sys.exit(-1)
#     for _p in _rp.split(os.path.pathsep):
#         if os.path.isdir(os.path.join(_p, 'pyradlib')):
#             if _p not in sys.path: sys.path.insert(0, _p)
#             break
#     else:
#         print('Support library not found on RAYPATH');
#         sys.exit(-1)

from pyRadLib.pyrad_proc import Error, ProcMixin


SHORTPROGN = os.path.splitext(os.path.basename(sys.argv[0]))[0]


lights = """
void glow dim 0 0 4 .1 .1 .15 0
dim source background 0 0 4 0 0 1 360
void light bright 0 0 3 1000 1000 1000
bright source sun1 0 0 4 1 .2 1 5
bright source sun2 0 0 4 .3 1 1 5
bright source sun3 0 0 4 -1 -.7 1 5"""


class Objview(ProcMixin):
    def __init__(self, args):
        self.useGl = args.useGl
        self.upDirection = args.upDirection
        self.backFaceVisible = args.backFaceVisible
        self.viewDetials = args.view_details
        self.numProc = args.numProc
        self.output_device = args.output_device
        self.verbose_display = args.verbose_display
        self.disable_warnings = args.disable_warnings
        self.gl_rad_full_screen = args.gl_rad_full_screen
        self.view_file = args.view_file
        self.scene_exposure = args.scene_exposure
        # Wrap all radfiles in quotes.
        self.rad_files = ['"%s"' % rad_file for rad_file in args.Radfiles[0]]
        self.no_lights = args.no_lights
        self.run_silently = args.run_silently
        self.print_viewsStdin = args.print_viewsStdin
        self.tempDir = None
        try:
            self.run()
        finally:
            if self.tempDir:
                shutil.rmtree(self.tempDir)

    def run(self):
        output_device = 'x11'
        if self.useGl and os.name == 'nt':
            self.raise_on_error("set glRad variables.",
                                "Glrad is only available in an X11 environment")

        self.create_temp()

        if not self.no_lights:
            self.rad_files.append(self.lightsFile)
        self.rad_options, self.render_options = self.create_rad_render_options()

        # If the OS is Windows then make the path Rad friendly by switching
        # slashes and set the output device to qt.
        if os.name == 'nt':
            self.rad_files = [s.replace('\\', '/') for s in self.rad_files]
            self.octree_file, self.lightsFile, self.rifFile, self.ambFile\
                = [
                    s.replace('\\', '/') for s in (self.octree_file, self.lightsFile,
                                                   self.rifFile, self.ambFile)]

            if self.view_file:
                self.view_file = [s.replace('\\', '/') for s in self.view_file]
            output_device = 'qt'

        self.rifLines = self.create_rif_list()
        self.write_files()

        if self.useGl:
            cmd_string = ['glrad'] + self.rad_options + [self.rifFile]
        else:
            if output_device:
                cmd_string = ['rad'] + ['-o', output_device] + \
                    self.rad_options + [self.rifFile]
            else:
                cmd_string = ['rad'] + self.rad_options + [self.rifFile]

        self.call_one(cmd_string, 'start rad')

    def create_temp(self):
        """Create temporary files and directories needed for objview"""
        # Try creating a temp folder. Exit if not possible.
        try:
            self.tempDir = tempfile.mkdtemp('RAD')
        except IOError as e:
            self.raise_on_error("Create a temp folder", e)

        # create strings for files that are to be written to.
        def create_in_temp(file_name):
            return os.path.join(self.tempDir, file_name)
        self.octree_file = create_in_temp('scene.oct')
        self.lightsFile = create_in_temp('lights.rad')
        self.rifFile = create_in_temp('scene.rif')
        self.ambFile = create_in_temp('scene.amb')

    def create_rad_render_options(self):
        """Based on the inputs provided, create options for running Rad/Glrad
        and also set rendering options."""

        # If the output device is specified by the user, use that.
        # TODO(sarith): I'm not sure what is happening here. What is the deal with
        # output_device. It doesn't get used after the assignement
        # if self.output_device:
        # output_device = self.output_device

        render_options = ''
        if self.backFaceVisible:
            render_options += '-bv '

        rad_options = []
        rad_options_set = False
        gl_rad_options_set = False
        if self.disable_warnings:
            rad_options.append("-w")
        if self.numProc:
            rad_options.extend(['-N', str(self.numProc)])
            rad_options_set = True
        if self.verbose_display:
            rad_options.append('-e')
            rad_options_set = True
        if self.gl_rad_full_screen:
            rad_options.append('-S')
            gl_rad_options_set = True
        if self.run_silently:
            rad_options.append('-s')
        if self.print_viewsStdin:
            rad_options.append('-V')
            rad_options_set = True

        if rad_options_set and self.useGl:
            self.raise_on_error("setting rad options",
                                'One among the following options :() are not '
                                'compatible with Open GL'.format(",".join(rad_options)))

        elif gl_rad_options_set and not self.useGl:
            self.raise_on_error('set glRad options.',
                                "Although glRad options have been set the "
                                "rendering is being run through RAD.")

        return rad_options, render_options

    def create_rif_list(self):
        """Create a list of RifFile variables based on user input and defaults."""
        rif_list = ['scene= %s' % s for s in self.rad_files]
        rif_list.append('EXPOSURE= %s' % (self.scene_exposure or 0.5))
        rif_list.append('UP= %s' % (self.upDirection or 'Z'))

        rif_list.append('OCTREE= %s' % self.octree_file)
        rif_list.append('AMBF= %s' % self.ambFile)
        rif_list.append('render=%s' % self.render_options)
        if self.view_file:
            self.view_file = '-vf %s' % "".join(self.view_file)
            rif_list.append('view= %s' % (self.view_file or ''))
        else:
            rif_list.append('view= %s' % (self.viewDetials or 'XYZ'))
        return rif_list

    def write_files(self):
        # Write lights and join to the input rad files.
        with open(self.lightsFile, 'w')as lightRad:
            lightRad.write(lights)

        with open(self.rifFile, 'w') as rifData:
            rifData.write('\n'.join(self.rifLines) + '\n')


def main():
    parser = argparse.ArgumentParser(add_help=False,
                                     description='Render a RADIANCE object '
                                                 'interactively')
    parser.add_argument('-g', action='store_true', dest='useGl',
                        help='Use OpenGL to render the scene')
    parser.add_argument('-u', action='store', dest='upDirection',
                        help='Up direction. The default '
                             'up direction vector is +Z',
                        type=str, metavar='upDirection')

    parser.add_argument('-bv', action='store_true', dest='backFaceVisible',
                        help='Enable back-face visibility in the scene.')
    parser.add_argument('-v', action='store', dest='view_details',
                        help='Specify view details.', type=str,
                        metavar='view_details')
    parser.add_argument('-N', action='store', dest='numProc',
                        help='Number of parallel processes to render the scene.',
                        type=int, metavar='numProc')
    parser.add_argument('-o', action='store', dest='output_device',
                        help='Specify an output device for rendering',
                        type=str, metavar='output_device')

    parser.add_argument('-w', action='store_true',
                        dest='disable_warnings',
                        help='Disable warnings about multiply and misassigned'
                             ' variables.')

    parser.add_argument('-s', action='store_true',
                        dest='run_silently',
                        help='Process the radiance scene silently')

    parser.add_argument('-S', action='store_true', dest='gl_rad_full_screen',
                        help='Enable full-screen stereo options with OpenGL')

    parser.add_argument('-exp', action='store',
                        dest='scene_exposure',
                        help='Set the exposure value')

    parser.add_argument('-e', action='store_true',
                        dest='verbose_display',
                        help='Display Radiance variables and  error messages in'
                             ' standard output')

    parser.add_argument('-V', action='store_true',
                        dest='print_viewsStdin',
                        help='Print each view on the standard output before being'
                             ' applied')

    parser.add_argument('Radfiles', action='append', nargs='+',
                        help='File(s) containing radiance scene objects that'
                             ' are to be rendered interactively.')

    parser.add_argument('-H', action='help', help='Help: print this text to '
                                                  'stderr and exit.')
    parser.add_argument('-vf', action='store', help='Specify a view file.',
                        dest='view_file')
    parser.add_argument('-nL', action='store_true', dest='no_lights',
                        help="Use lights in the scene only. Don't add additional lights")

    Objview(parser.parse_args())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write('*cancelled*\n')
        sys.exit(1)
    except (Error) as e:
        sys.stderr.write('%s: %s\n' % (SHORTPROGN, str(e)))
        sys.exit(-1)
