"""A collection of auxiliary funtions for working with files and directories."""
import os


def preparedir(targetDir):
    """Prepare a folder for analysis.

    This method creates the folder if it is not created, and removes the file in
    the folder if the folder already existed.
    """
    if os.path.isdir(targetDir):
        nukedir(targetDir, False)
    else:
        try:
            os.mkdir(targetDir)
        except Exception as e:
            print "Failed to create folder: %s\n%s" % (targetDir, e)
            return False
    return True


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
