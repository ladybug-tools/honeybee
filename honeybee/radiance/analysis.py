"""Radiance Analysis workflows."""
from subprocess import Popen
import time
import os


# TODO: (@sariths) Should we add electrical lighting as an input in rad files.
class AnalysisBase(object):
    """Base analysis class for Radiance analysis."""

    def __init__(self, HBObjects, analysisRecipe, otherRADFiles=None):
        """Create an analysis by HBSky and HBObjects.

        Args:
            HBSky: A honeybee.radiance.sky
            analysisRecipe: A honeybee.radiance.analysisRecipe
            HBObjects: A list of Honeybee surfaces or zones
            otherRADFiles: An ordered list of additional radiance file to be
                added to the analysis.
        """
        self.__isExecuted = False
        self.__done = False

    @property
    def isRunning(self):
        """Return is analysis is still running."""
        if not self.__isExecuted:
            return False
        return not self.__done

    @property
    def isOver(self):
        """Return if analysis is done."""
        return self.__done

    @property
    def progress(self):
        """Return progress value between 0-100."""
        raise NotImplementedError

    def write(self):
        """Write analysis files."""
        raise NotImplementedError

    def run(self, minimize=False):
        """Run analysis."""
        self.__isExecuted = True
        self.__executeBatchFiles(minimize=minimize)

    def results(self):
        """Get analysis results."""
        pass

    def __executeBatchFiles(self, batchFiles, maxPRuns=None, minimize=False,
                            waitingTime=0.5):
        """Run a list of batch files in parallel.

        Args:
            batchFiles: List of batch files.
            maxPRuns: Max number of files to be ran in parallel (default: 1).
            minimize: Set to True if you want NOT to see the cmd window.
        """
        if not maxPRuns:
            maxPRuns = 1
        maxPRuns = int(maxPRuns)
        total = len(batchFiles)

        if maxPRuns < 1:
            maxPRuns = 1
        if maxPRuns > total:
            maxPRuns = total

        running = 0
        self.__done = False
        jobs = []
        pid = 0

        try:
            while not self.__done:
                if running < maxPRuns and pid < total:
                    # execute the files
                    jobs.append(Popen(os.path.normpath(batchFiles[pid]), shell=minimize))
                    pid += 1
                    time.sleep(waitingTime)

                # count how many jobs are running and how many are done
                running = 0
                finished = 0
                for job in jobs:
                    if job.poll() is None:
                        # one job is still running
                        running += 1
                    else:
                        finished += 1

                if running == maxPRuns:
                    # wait for half a second
                    time.sleep(waitingTime)

                if finished == total:
                    self.__done = True

        except Exception, e:
            print "Failed to execute batch files: %s" % str(e)

    def __repr__(self):
        """Represent Analysis class."""
        return "honeybee.Analysis.%s" % self.__class__.__name__
