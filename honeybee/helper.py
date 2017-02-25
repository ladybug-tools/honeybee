"""A collection of auxiliary funtions for working with files and directories."""
import os
import shutil
import config


def normspace(path):
    """Norm white spaces in path.

    Return path with quotation marks if there is whitespace in path.
    """
    if str(path).strip().find(" ") != -1:
        return "{0}{1}{0}".format(config.wrapper, path)
    else:
        return path


def getRadiancePathLines():
    """Return path to radiance folders."""
    if config.radbinPath.find(' ') != -1:
        msg = 'Radiance path {} has a whitespace. Some of the radiance ' \
            'commands may fail.\nWe strongly suggest you to install radiance ' \
            'under a path with no withspace (e.g. c:/radiance)'.format(
                self.radbinPath
            )
        print msg
    if os.name == 'nt':
        return "SET RAYPATH=.;{}\nPATH={};$PATH".format(
            normspace(config.radlibPath),
            normspace(config.radbinPath))
    else:
        return ""


def preparedir(targetDir, removeContent=True):
    """Prepare a folder for analysis.

    This method creates the folder if it is not created, and removes the file in
    the folder if the folder already existed.
    """
    if os.path.isdir(targetDir):
        if removeContent:
            nukedir(targetDir, False)
        return True
    else:
        try:
            os.makedirs(targetDir)
            return True
        except Exception as e:
            print "Failed to create folder: %s\n%s" % (targetDir, e)
            return False


def nukedir(targetDir, rmdir=False):
    """Delete all the files inside targetDir.

    Usage:
        nukedir("c:/ladybug/libs", True)
    """
    d = os.path.normpath(targetDir)

    if not os.path.isdir(d):
        return

    files = os.listdir(d)

    for f in files:
        if f == '.' or f == '..':
            continue
        path = os.path.join(d, f)

        if os.path.isdir(path):
            nukedir(path)
        else:
            try:
                os.remove(path)
            except:
                print "Failed to remove %s" % path

    if rmdir:
        try:
            os.rmdir(d)
        except:
            print "Failed to remove %s" % d


def writeToFile(filePath, data, mkdir=False):
    """Write a string of data to file.

    Args:
        filePath: Full path for a valid file path (e.g. c:/ladybug/testPts.pts)
        data: Any data as string
        mkdir: Set to True to create the directory if doesn't exist (Default: False)
    """
    __dir, __name = os.path.split(filePath)

    if not os.path.isdir(__dir):
        if mkdir:
            preparedir(__dir)
        else:
            raise ValueError("Failed to find %s." % __dir)

    with open(filePath, "w") as outf:
        try:
            outf.write(str(data))
            return filePath
        except Exception as e:
            raise IOError("Failed to write %s to file:\n\t%s" % (__name, str(e)))


def copyFilesToFolder(files, targetFolder, overwrite=True):
    """Copy a list of files to a new target folder.

    Returns:
        A list of fullpath of the new files.
    """
    if not files:
        return []

    for f in files:
        target = os.path.join(targetFolder, os.path.split(f)[-1])

        if target == f:
            # both file path are the same!
            return target

        if os.path.exists(target):
            if overwrite:
                # remove the file before copying
                try:
                    os.remove(target)
                except:
                    raise IOError("Failed to remove %s" % f)
                else:
                    shutil.copy(f, target)
            else:
                continue
        else:
            print 'copying %s to %s' % (os.path.split(f)[-1], targetFolder)
            shutil.copy(f, targetFolder)

    return [os.path.join(targetFolder, os.path.split(f)[-1]) for f in files]
