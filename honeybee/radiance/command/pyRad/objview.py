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
        self.viewDetials = args.viewDetails
        self.numProc = args.numProc
        self.outputDevice = args.outputDevice
        self.verboseDisplay = args.verboseDisplay
        self.disableWarnings = args.disableWarnings
        self.glRadFullScreen = args.glRadFullScreen
        self.viewFile = args.viewFile
        self.sceneExposure = args.sceneExposure
        #Wrap all radfiles in quotes.
        self.radFiles =['"%s"'%radFile for radFile in args.Radfiles[0]]
        self.noLights = args.noLights
        self.runSilently = args.runSilently
        self.printViewsStdin = args.printViewsStdin
        self.tempDir = None
        try: self.run()
        finally:
            if self.tempDir:
                shutil.rmtree(self.tempDir)

    def run(self):
        outputDevice = 'x11'
        if self.useGl and os.name == 'nt':
            self.raise_on_error("set glRad variables.",
                    "Glrad is only available in an X11 environment")

        self.createTemp()

        if not self.noLights:
            self.radFiles.append(self.lightsFile)
        self.radOptions, self.renderOptions = self.createRadRenderOptions()

        # If the OS is Windows then make the path Rad friendly by switching
        # slashes and set the output device to qt.
        if os.name == 'nt':
            self.radFiles = [s.replace('\\', '/') for s in self.radFiles]
            self.octreeFile, self.lightsFile, self.rifFile, self.ambFile\
                = [
                s.replace('\\', '/') for s in (self.octreeFile,self.lightsFile,
                                               self.rifFile, self.ambFile)]

            if self.viewFile:
                self.viewFile = [s.replace('\\', '/') for s in self.viewFile]
            outputDevice = 'qt'


        self.rifLines = self.createRifList()
        self.writeFiles()

        if self.useGl:
            cmdString = ['glrad']+self.radOptions+[self.rifFile]
        else:
            if outputDevice:
                cmdString = ['rad']+['-o',outputDevice]+self.radOptions+[self.rifFile]
            else:
                cmdString = ['rad'] +  self.radOptions + [self.rifFile]

        self.call_one(cmdString,'start rad')

    def createTemp(self):
        """Create temporary files and directories needed for objview"""
        # Try creating a temp folder. Exit if not possible.
        try:
            self.tempDir = tempfile.mkdtemp('RAD')
        except IOError as e:
            self.raise_on_error("Create a temp folder",e)

        # create strings for files that are to be written to.
        createInTemp = lambda fileName: os.path.join(self.tempDir, fileName)
        self.octreeFile = createInTemp('scene.oct')
        self.lightsFile = createInTemp('lights.rad')
        self.rifFile = createInTemp('scene.rif')
        self.ambFile = createInTemp('scene.amb')

    def createRadRenderOptions(self):
        """Based on the inputs provided, create options for running Rad/Glrad
        and also set rendering options."""

        # If the output device is specified by the user, use that.
        if self.outputDevice:
            outputDevice = self.outputDevice

        renderOptions = ''
        if self.backFaceVisible:
            renderOptions += '-bv '

        radOptions = []
        radOptionsSet = False
        glRadOptionsSet = False
        if self.disableWarnings:
            radOptions.append("-w")
        if self.numProc:
            radOptions.extend(['-N', str(self.numProc)])
            radOptionsSet = True
        if self.verboseDisplay:
            radOptions.append('-e')
            radOptionsSet = True
        if self.glRadFullScreen:
            radOptions.append('-S')
            glRadOptionsSet = True
        if self.runSilently:
            radOptions.append('-s')
        if self.printViewsStdin:
            radOptions.append('-V')
            radOptionsSet = True

        if radOptionsSet and self.useGl:
            self.raise_on_error("setting rad options",
                                'One among the following options :() are not '
                                'compatible with Open GL'.format(",".join(radOptions)))

        elif glRadOptionsSet and not self.useGl:
            self.raise_on_error('set glRad options.',
                                 "Although glRad options have been set the "
                                 "rendering is being run through RAD.")

        return radOptions,renderOptions

    def createRifList(self):
        """Create a list of RifFile variables based on user input and defaults."""
        rifList = ['scene= %s' % s for s in self.radFiles]
        rifList.append('EXPOSURE= %s'%(self.sceneExposure or 0.5))
        rifList.append('UP= %s' % (self.upDirection or 'Z'))

        rifList.append('OCTREE= %s' % self.octreeFile)
        rifList.append('AMBF= %s' % self.ambFile)
        rifList.append('render=%s' % self.renderOptions)
        if self.viewFile:
            self.viewFile = '-vf %s'%"".join(self.viewFile)
            rifList.append('view= %s'%(self.viewFile or ''))
        else:
            rifList.append('view= %s' % (self.viewDetials or 'XYZ'))
        return rifList

    def writeFiles(self):
        # Write lights and join to the input rad files.
        with open(self.lightsFile, 'w')as lightRad:
            lightRad.write(lights)

        with open(self.rifFile, 'w') as rifData:
            rifData.write('\n'.join(self.rifLines) + '\n')


def main():
    parser = argparse.ArgumentParser(add_help=False,
                                     description='Render a RADIANCE object ' \
                                                 'interactively')
    parser.add_argument('-g', action='store_true', dest='useGl',
                        help='Use OpenGL to render the scene')
    parser.add_argument('-u', action='store', dest='upDirection',
                        help='Up direction. The default '
                             'up direction vector is +Z',
                        type=str, metavar='upDirection')

    parser.add_argument('-bv', action='store_true', dest='backFaceVisible',
                        help='Enable back-face visibility in the scene.')
    parser.add_argument('-v', action='store', dest='viewDetails',
                        help='Specify view details.', type=str,
                        metavar='viewDetails')
    parser.add_argument('-N', action='store', dest='numProc',
                        help='Number of parallel processes to render the scene.',
                        type=int, metavar='numProc')
    parser.add_argument('-o', action='store', dest='outputDevice',
                        help='Specify an output device for rendering',
                        type=str, metavar='outputDevice')

    parser.add_argument('-w', action='store_true',
                        dest='disableWarnings',
                        help='Disable warnings about multiply and misassigned'
                             ' variables.')

    parser.add_argument('-s', action='store_true',
                        dest='runSilently',
                        help='Process the radiance scene silently')

    parser.add_argument('-S',action='store_true',dest='glRadFullScreen',
                        help='Enable full-screen stereo options with OpenGL')
						
    parser.add_argument('-exp', action='store',
                        dest='sceneExposure',
                        help='Set the exposure value')
							 
    parser.add_argument('-e', action='store_true',
                        dest='verboseDisplay',
                        help='Display Radiance variables and  error messages in'
                             ' standard output')

    parser.add_argument('-V', action='store_true',
                        dest='printViewsStdin',
                        help='Print each view on the standard output before being'
                             ' applied')

    parser.add_argument('Radfiles', action='append', nargs='+',
                        help='File(s) containing radiance scene objects that'
                             ' are to be rendered interactively.')

    parser.add_argument('-H', action='help', help='Help: print this text to '
                                                  'stderr and exit.')
    parser.add_argument('-vf',action='store',help='Specify a view file.',
                        dest='viewFile')
    parser.add_argument('-nL',action='store_true',dest='noLights',
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
