"""A collection of useful methods for recipes."""
from ..command.rfluxmtx import Rfluxmtx
from ..command.dctimestep import Dctimestep
from ..command.rmtxop import Rmtxop
from ..command.gendaymtx import Gendaymtx

import os


def coeffMatrixCommands(outputName, receiver, radFiles, sender, pointsFile=None,
                        numberOfPoints=None, samplingRaysCount=None,
                        rfluxmtxParameters=None):
    """Returns radiance commands to create coefficient matrix.

    Args:
        outputName: Output file name.
        receiver: A radiance file to indicate the receiver. In view matrix it will be the
        window group and in daylight matrix it will be the sky.
        radFiles: A collection of Radiance files that should be included in the scene.
        sender: A collection of files for senders if senders are radiance geometries
            such as window groups (Default: '-').
        pointsFile: Path to point file which will be used instead of sender.
        numberOfPoints: Number of points in pointsFile as an integer.
        samplingRaysCount: Number of sampling rays (Default: 1000).
        rfluxmtxParameters: Radiance parameters for Rfluxmtx command using a
            RfluxmtxParameters instance (Default: None).
    """
    sender = sender or '-'
    radFiles = radFiles or ()
    numberOfPoints = numberOfPoints or 0
    rfluxmtx = Rfluxmtx()

    if sender == '-':
        assert pointsFile, \
            ValueError('You have to set the pointsFile when sender is not defined.')

    # -------------- set the parameters ----------------- #
    rfluxmtx.rfluxmtxParameters = rfluxmtxParameters
    # ray counts
    if samplingRaysCount:
        rfluxmtx.samplingRaysCount = samplingRaysCount

    # -------------- set up the sender objects ---------- #
    # '-' in case of view matrix, window group in case of
    # daylight matrix. This is normally the receiver file
    # in view matrix
    rfluxmtx.sender = sender

    # points file are the senders in view matrix
    rfluxmtx.numberOfPoints = numberOfPoints
    rfluxmtx.pointsFile = pointsFile

    # --------------- set up the  receiver --------------- #
    # This will be the window for view matrix and the sky for
    # daylight matrix. It makes sense to make a method for each
    # of thme as they are pretty repetitive
    # Klems full basis sampling
    rfluxmtx.receiverFile = receiver

    # ------------- add radiance geometry files ----------------
    # For view matrix it's usually the room itself and the materials
    # in case of each view analysis rest of the windows should be
    # blacked! In case of daylight matrix it will be the context
    # outside the window.
    rfluxmtx.radFiles = radFiles

    # output file address/name
    rfluxmtx.outputMatrix = outputName

    return rfluxmtx


def windowGroupToReceiver(filepath, upnormal):
    """Take a filepath to a window group and create a receiver."""
    recCtrlPar = Rfluxmtx.controlParameters(hemiType='kf', hemiUpDirection=upnormal)
    wg_m = Rfluxmtx.addControlParameters(filepath, {'vmtx_glow': recCtrlPar})
    return wg_m


def skyReceiver(filepath, density):
    """Create a receiver sky for daylight coefficient studies."""
    return Rfluxmtx.defaultSkyGround(filepath, skyType='r{}'.format(density))


def matrixCalculation(output, vMatrix=None, tMatrix=None, dMatrix=None, skyMatrix=None):
    """Get commands for matrix calculation.

    This method sets up a matrix calculations using Dctimestep.
    """
    dct = Dctimestep()
    dct.tmatrixFile = tMatrix
    dct.vmatrixSpec = vMatrix
    dct.dmatrixFile = dMatrix
    dct.skyVectorFile = skyMatrix
    dct.outputFile = output
    return dct


def convertMatrixResults(output, input):
    """Convert rgb values in matrix to illuminance values."""
    finalmtx = Rmtxop(matrixFiles=input, outputFile=output)
    finalmtx.rmtxopParameters.outputFormat = 'a'
    finalmtx.rmtxopParameters.combineValues = (47.4, 119.9, 11.6)
    finalmtx.rmtxopParameters.transposeMatrix = False
    return finalmtx


def skymtxToGendaymtx(skyMatrix, targetFolder):
    """Return a gendaymtx command based on input skyMatrix."""
    weaFilepath = 'skies\\{}.wea'.format(skyMatrix.name)
    skyMtx = 'skies\\{}.smx'.format(skyMatrix.name)
    hoursFile = os.path.join(targetFolder, 'skies\\{}.hrs'.format(skyMatrix.name))

    if not os.path.isfile(os.path.join(targetFolder, skyMtx)) \
            or not os.path.isfile(os.path.join(targetFolder, weaFilepath)) \
            or not skyMatrix.hoursMatch(hoursFile):
        # write wea file to folder
        skyMatrix.writeWea(os.path.join(targetFolder, 'skies'), writeHours=True)
        gdm = Gendaymtx(outputName=skyMtx, weaFile=weaFilepath)
        gdm.gendaymtxParameters.skyDensity = skyMatrix.skyDensity
        return gdm
