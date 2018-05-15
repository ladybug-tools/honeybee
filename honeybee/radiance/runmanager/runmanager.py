"""Radiance Analysis workflows."""
import time
import os


class TaskGroup(object):
    """A group of radiance tasks which will be executed in parallel."""

    def __init__(self, tasks=None):
        self._tasks = tasks or ()

    @property
    def is_finished(self):
        for task in self._tasks:
            if not task.is_finished:
                return False
        return True

    @property
    def progress(self):
        for task in self._tasks:
            print('..%s' % task.progress_report)

    def execute(self, cpus=1, cwd=None, env=None, update_freq=5, verbose=True):
        """Execute tasks in this task group in parallel."""
        # execute first subtasks
        running = [None for task in self._tasks]
        for count, task in enumerate(self._tasks):
            if verbose:
                print('..Starting task {}'.format(task.title))
            running[count] = task.execute_next(cwd, env, verbose)

        while not self.is_finished:
            for count in xrange(len(self._tasks)):
                if not running[count]:
                    # no extra task is left in this task group
                    continue
                if running[count].is_finished:
                    # report success or failure
                    print(running[count].progress_report)
                    if not running[count].is_succeed:
                        # kill all the other runs
                        return -1
                    # execute next task read to go
                    running[count] = self._tasks[count].execute_next(cwd, env, verbose)
                else:
                    print('{}'.format(running[count].progress_report))
                time.sleep(update_freq)

    def terminate(self):
        """Terminate task group."""
        for task in self._tasks:
            if task.is_running:
                task.terminate()


# TODO(mostapha): Keep track of number of cpus
# TODO(mostapha): enhance reporting.
class Runner(object):
    """Run manager for Radiance tasks."""

    def __init__(self, title, tasks):
        """Run manager for Radiance tasks.

        Args:
            tasks: List of lists of tasks to execute. Grouped tasks will be executed
                in parallel. Each group will be executed in serial. For isinstance
                for ((task_1, task_2), task_3) input Runner will execute task_1 and
                task_2 in parallel and executes task_3 only when both task_1 and task_2
                is finished.
        """
        self._title = title
        self._taskgroups = [TaskGroup(task) for task in tasks]

    def execute(self, cpus=1, cwd=None, env=None, update_freq=5, verbose=True):
        """Execute all task groups."""
        if verbose:
            print('Starting {}'.format(self._title))
        for taskgroup in self._taskgroups:
            # this is a blocking call
            success = taskgroup.execute(cpus, cwd, env, update_freq, verbose)
            if success == -1:
                # task has failed
                print('Terminating running tasks...')
                taskgroup.terminate()
                return

    def __repr__(self):
        """Represent Runner class."""
        return 'RunManager: {}'.format(self._title)
