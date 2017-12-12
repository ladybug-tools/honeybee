"""Radiance Analysis workflows."""
from subprocess import Popen
import time
import os


# TODO: (@sariths) Should we add electrical lighting as an input in rad files.
class AnalysisBase(object):
    """Base analysis class for Radiance analysis."""

    def __init__(self, hb_objects, analysis_recipe, other_rad_files=None):
        """Create an analysis by HBSky and hb_objects.

        Args:
            HBSky: A honeybee.radiance.sky
            analysis_recipe: A honeybee.radiance.analysis_recipe
            hb_objects: A list of Honeybee surfaces or zones
            other_rad_files: An ordered list of additional radiance file to be
                added to the analysis.
        """
        self.__isExecuted = False
        self.__done = False

    @property
    def is_running(self):
        """Return is analysis is still running."""
        if not self.__isExecuted:
            return False
        return not self.__done

    @property
    def is_over(self):
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
        self.__execute_batch_files(minimize=minimize)

    def results(self):
        """Get analysis results."""
        pass

    def __execute_batch_files(self, batch_files, max_p_runs=None, minimize=False,
                              waiting_time=0.5):
        """Run a list of batch files in parallel.

        Args:
            batch_files: List of batch files.
            max_p_runs: Max number of files to be ran in parallel (default: 1).
            minimize: Set to True if you want NOT to see the cmd window.
        """
        if not max_p_runs:
            max_p_runs = 1
        max_p_runs = int(max_p_runs)
        total = len(batch_files)

        if max_p_runs < 1:
            max_p_runs = 1
        if max_p_runs > total:
            max_p_runs = total

        running = 0
        self.__done = False
        jobs = []
        pid = 0

        try:
            while not self.__done:
                if running < max_p_runs and pid < total:
                    # execute the files
                    jobs.append(
                        Popen(
                            os.path.normpath(
                                batch_files[pid]),
                            shell=minimize))
                    pid += 1
                    time.sleep(waiting_time)

                # count how many jobs are running and how many are done
                running = 0
                finished = 0
                for job in jobs:
                    if job.poll() is None:
                        # one job is still running
                        running += 1
                    else:
                        finished += 1

                if running == max_p_runs:
                    # wait for half a second
                    time.sleep(waiting_time)

                if finished == total:
                    self.__done = True

        except Exception as e:
            print("Failed to execute batch files: %s" % str(e))

    def __repr__(self):
        """Represent Analysis class."""
        return "honeybee.Analysis.%s" % self.__class__.__name__
