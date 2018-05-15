"""Radiance Task.

A task is a series of command that will be executed one after each other.
"""
import re
import subprocess
import os
import time


class Task(object):
    """A collection of subtasks to be executed one after each other."""

    def __init__(self, title, subtasks):
        self._cpu_demand = 1  # will be overwritten based on input tasks.
        self._title = title
        self._last_task_executed = None
        self.subtasks = subtasks

    @classmethod
    def from_json(cls, task_json):
        """Create a task from a dictionary.

        {'title': self._title, 'subtasks': [{}, {}]}
        """
        return cls(task_json['title'],
                   SubTask.from_json(st for st in task_json['subtasks']))

    @property
    def title(self):
        """SubTask title."""
        return self._title

    @property
    def cpu_demand(self):
        """Number of cpus that this task will be using.

        This number will always be 1 on Windows as radiance doesn't support
        multi-processor calculation on Windows.
        """
        return self._cpu_demand

    @property
    def subtasks(self):
        """List of subtasks."""
        return self._subtasks

    @subtasks.setter
    def subtasks(self, input):
        for task in input:
            assert isinstance(task, SubTask), 'Expected SubTask not {}.'.format(task)
            self._cpu_demand = max(task.cpu_demand, self._cpu_demand)

        self._subtasks = input

    @property
    def count(self):
        """Length of subtasks."""
        return len(self.subtasks)

    @property
    def is_running(self):
        for subtask in self.subtasks:
            if subtask.is_running:
                return True
        return False

    @property
    def is_finished(self):
        """Check if the execution of this task is finished."""
        for subtask in self.subtasks:
            if not subtask.is_finished:
                return False
        return True

    def is_succeed(self):
        """True if all subtasks are executed successfully."""
        for subtask in self.subtasks:
            if not subtask.is_succeed:
                return False
        return True

    @property
    def progress_report(self):
        """Return human readable progress of subtasks."""
        for task in self.subtasks:
            print('....%s' % task.progress_report)

    def execute(self, cwd=None, env=None, verbose=True, update_freq=5):
        """Execute this taskself.

        This method is blocking and will wait until the execution is finished.
        """
        for count in range(self.count):
            task = self.execute_subtask(count, cwd, env, verbose)
            while task.is_running:
                if verbose:
                    # replace eith progress
                    print('....[{} of {}]: {}'.format(
                        count + 1, self.count, task.progress_report))
                time.sleep(update_freq)
            # report success or failure
            if not task.is_succeed:
                print('....[{} of {}]: {}'.format(count + 1,
                                                  self.count,
                                                  task.progress_report))
                break

    def execute_subtask(self, task_index, cwd=None, env=None, verbose=True):
        task = self.subtasks[task_index]
        if verbose:
            print('...Starting subtask {} of {}: {}...'.format(
                task_index + 1, self.count, task.title))
        task.execute(cwd, env)
        self._last_task_executed = task_index
        return task

    def execute_next(self, cwd=None, env=None, verbose=True):
        """Execute next task in line."""
        if self._last_task_executed and self._last_task_executed + 1 == self.count:
            return

        if self._last_task_executed is None:
            task_index = 0
        else:
            task_index = self._last_task_executed + 1

        task = self.subtasks[task_index]
        if verbose:
            print('...Starting subtask {} of {}: {}...'.format(
                task_index + 1, self.count, task.title))
        task.execute(cwd, env)
        self._last_task_executed = task_index
        return task

    def terminate(self):
        """Terminate subtask."""
        for subtask in self.subtasks:
            if subtask.is_running:
                subtask.terminate()

    def to_json(self):
        """Return a Task as a dictionary."""

        return {'title': self.title,
                'subtasks': [task.to_json() for task in self.subtasks]}

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Task representation."""
        return '\n'.join('{}: {}'.format(count + 1, task.title)
                         for count, task in enumerate(self.subtasks))


class SubTask(object):

    def __init__(self, title, command, output_file=None, expected_output_size=None):
        """Task

        Args:
            title: Human readable title for this command.
            command: A radinace command as strings.
            output_file: Relative path to output_file. This file will be used to report
                completion process.
            expected_output_size: Expected output size for output file. This number will
                be used to report completion process.
        """
        self._title = title
        self._command = command
        self._cpu_demand = self._get_cpu_count(command)
        self._process = None
        self._output_file = output_file
        self._expected_size = expected_output_size
        self._execution_started_at = None

    @classmethod
    def from_json(cls, task_json):
        """Create a task from a dictionary.

        {'title': self._title, 'command': self.command}
        """
        if 'output_file' in task_json:
            output_file = task_json['output_file']
        else:
            output_file = None
        if 'output_file' in task_json:
            expected_size = task_json['expected_size']
        else:
            expected_size = None

        return cls(task_json['title'], task_json['command'], output_file, expected_size)

    @property
    def title(self):
        """SubTask title."""
        return self._title

    @property
    def cpu_demand(self):
        """Number of cpus that this task will be using.

        This number will always be 1 on Windows as radiance doesn't support
        multi-processor calculation on Windows.
        """
        return self._cpu_demand

    @property
    def is_started(self):
        if self._process:
            return True
        else:
            return False

    @property
    def is_running(self):
        if self._process:
            return self._process.poll() is None
        else:
            return False

    @property
    def is_finished(self):
        if self._process:
            return not self._process.poll() is None
        else:
            return False

    @property
    def is_succeed(self):
        if self._process:
            return self._process.returncode == 0
        else:
            return False

    @property
    def command(self):
        """List of command for this task."""
        return self._command

    @property
    def progress(self):
        """Progress as a percentage."""
        if not self.is_started:
            return 0
        elif not self._output_file or not self._expected_size:
            return -1
        elif not os.path.isfile(self._output_file):
            return -1
        else:
            count = os.path.getsize(self._output_file)
            percent = min(100, round(100.0 * count / float(self._expected_size), 1))
            return percent

    @property
    def progress_report(self):
        """Human readable progress report."""
        if not self.is_started:
            return '...{} is not started!'.format(self.title)
        elif self.is_finished:
            if self.is_succeed:
                return '...Finished {} successfully!'.format(self.title)
            else:
                # the task failed for some reason
                return '...{} failed:\n\n\tError message:\n\t{}\n\tCommand:\n\t{}' \
                    .format(self.title, '\t'.join(self.stderr), self.command)
        else:
            # it is still running
            progress = self.progress
            if progress == -1:
                return '....{0} is still running ({1:.2f}s).'.format(
                    self.title, time.time() - self._execution_started_at
                )
            else:
                return '....{0} is {1}% complete in {2:.2f}s.'.format(
                    self.title, self.progress, time.time() - self._execution_started_at
                )

    @property
    def stderr(self):
        """Return standard errors if any."""
        if self._process:
            return self._process.stderr
        else:
            return ()

    @property
    def stdout(self):
        """Return standard output if any."""
        if self._process:
            return self._process.stdout
        else:
            return ()

    @staticmethod
    def _get_cpu_count(command):
        """Get number of cpus from command.

        This method tries to find the digit after -n in command and return the max
        number.
        """
        n = 1
        result = re.findall(r'-n\s*(\d)', command)
        for num_cpu in result:
            if int(num_cpu) > n:
                n = num_cpu
        return n

    def execute(self, cwd=None, env=None):
        """Execute command one after each other."""
        self._execution_started_at = time.time()
        if cwd and self._output_file and cwd not in self._output_file:
            self._output_file = os.path.join(cwd, self._output_file)

        self._process = subprocess.Popen(
            self.command, cwd=cwd, env=env,
            stderr=subprocess.PIPE, stdout=subprocess.PIPE,
            shell=True
        )

    def terminate(self):
        """Terminate subtask."""
        if not self.is_started:
            return
        elif self.is_running:
            self._process.terminate()

    def to_json(self):
        """Return a Task as a dictionary."""

        return {'title': self.title, 'command': self.command,
                'output_file': self._output_file,
                'expected_size': self._expected_size}

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Task representation."""
        return 'SubTask: %s' % self.command
