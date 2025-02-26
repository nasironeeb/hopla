##########################################################################
# Hopla - Copyright (C) AGrigis, 2015 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Contains PBS specific functions.
"""

import os
import json
import time
import warnings
import subprocess
from pathlib import Path
from .utils import JobPaths


class PbsInfoWatcher:
    """ An instance of this class is shared by all jobs, and is in charge of
    calling pbs to check status for all jobs at once.

    Parameters
    ----------
    delay_s: int, default 60
        maximum delay before each non-forced call to the cluster.
    """
    def __init__(self, delay_s=60):
        self._delay_s = delay_s
        self._last_status_check = time.time()
        self._output = b""
        self._num_calls = 0
        self._info_dict = {}
        self._registered = set()
        self._finished = set()

    def clear(self):
        """ Clears cache.
        """
        self._last_status_check = time.time()
        self._output = b""
        self._num_calls = 0
        self._info_dict = {}
        self._registered = set()
        self._finished = set()

    def get_info(self, job_id):
        """ Returns a dict containing info about the job.

        Parameters
        ----------
        job_id: int
            id of the job on the cluster.
        """
        if job_id not in self._registered:
            self.register_job(job_id)
        last_check_delta = time.time() - self._last_status_check
        if last_check_delta > self._delay_s:
            self.update()
        return self._info_dict.get(job_id, {})

    def update(self):
        """ Updates the info of all registered jobs with a call to qstat.
        """
        if len(self._registered) == 0:
            return
        active_jobs = self._registered - self._finished
        command = "qstat -fx -F json " + " ".join(active_jobs)
        self._num_calls += 1
        try:
            self._output = subprocess.check_output(command, shell=True)
        except Exception as e:
            warnings.warn(
                f"Call #{self._num_calls} - Bypassing qstat error {e}, status "
                "may be inaccurate."
            )
        else:
            self._info_dict.update(self.read_info(self._output))
        self._last_status_check = time.time()
        for job_id in active_jobs:
            if self.is_done(job_id):
                self._finished.add(job_id)

    def get_state(self, job_id):
        """ Returns the state of the job.

        Parameters
        ----------
        job_id: str
            id of the job on the cluster.
        """
        info = self.get_info(job_id)
        return info.get("job_state") or "UNKNOWN"

    def is_done(self, job_id):
        """ Returns whether the job is finished.

        Parameters
        ----------
        job_id: str
            id of the job on the cluster.
        """
        state = self.get_state(job_id)
        return state.upper() not in ["R", "Q", "S", "UNKNOWN"]

    def read_info(self, string):
        """ Reads the output of qstat and returns a dictionary containing
        main jobs information.
        """
        if not isinstance(string, str):
            string = string.decode()
        all_stats = dict((key.split(".")[0], val)
                         for key, val in json.loads(string)["Jobs"].items())
        return all_stats

    def register_job(self, job_id):
        """ Register a job on the instance for shared update.
        """
        assert isinstance(job_id, str), f"{job_id} - {type(job_id)}"
        self._registered.add(job_id)


class DelayedPbsJob:
    """ Represents a job that have been queue for submission by an executor,
    but hasn't yet been scheduled.

    Parameters
    ----------
    delayed_submission: DelayedSubmission
        a delayed submission alowwing the generate the command line to
        execute.
    executor: Executor
        base job executor.
    job_id: str
        the job identifier.
    """
    def __init__(self, delayed_submission, executor, job_id):
        self.delayed_submission = delayed_submission
        self._executor = executor
        self.job_id = job_id
        self.submission_id = None
        self.paths = JobPaths(self._executor.folder, self.job_id)
        path = Path(__file__).parent / "pbs_batch_template.txt"
        with open(path, "rt") as of:
            self.template = of.read()

    def generate_batch(self):
        """ Write the batch file.
        """
        with open(self.paths.submission_file, "w") as of:
            if self.paths.stdout.exists():
                os.remove(self.paths.stdout)
            if self.paths.stderr.exists():
                os.remove(self.paths.stderr)
            of.write(self.template.format(
                command=self.delayed_submission.command,
                stdout=self.paths.stdout,
                stderr=self.paths.stderr,
                **self._executor.parameters))

    def start(self):
        """ Start a job.
        """
        self.generate_batch()
        if self.submission_id is None or self.done:
            process = subprocess.Popen(["qsub", self.paths.submission_file],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            stdout = stdout.decode("utf8")
            self.submission_id = stdout.rstrip("\n").split(".")[0]
            # print(f"Job {self.submission_id} - {self.paths.submission_file} "
            #       "is running!")
            self._register_in_watcher()

    def stop(self):
        """ Stop a job.
        """
        if self.submission_id is not None or not self.done:
            cmd = ["qdel", self.job_id]
            subprocess.check_call(cmd)

    @property
    def done(self):
        """ Checks whether the job is finished properly.
        """
        if self.submission_id is None:
            return False
        return self._executor.watcher.is_done(self.submission_id)

    @property
    def status(self):
        """ Checks the job status.
        """
        if self.submission_id is None:
            return "NOTSTARTED"
        return self._executor.watcher.get_state(self.submission_id)

    @property
    def exitcode(self):
        """ Check if the code finished properly.
        """
        if self.paths.stdout.exists():
            with open(self.paths.stdout, "rt") as of:
                return of.readlines()[-1].strip("\n") == "DONE"
        return False

    def _register_in_watcher(self):
        self._executor.watcher.register_job(self.submission_id)

    @property
    def report(self):
        """ Generate a report for the submitted job.
        """
        message = ["-" * 40]
        code = "sucess" if self.exitcode else "failure"
        prefix = f"{self.__class__.__name__}<job_id={self.job_id}>"
        message.append(f"{prefix}exitcode: {code}")
        if self.paths.submission_file.exists():
            message.append(f"{prefix}submission: {self.paths.submission_file}")
        else:
            message.append(f"{prefix}submission: none")
        if self.paths.stdout.exists():
            message.append(f"{prefix}stdout: {self.paths.stdout}")
            with open(self.paths.stdout, "rt") as of:
                info = [line.strip("\n") for line in of.readlines()]
            message.append(f"{prefix}submission_id: {info[0]}")
            message.append(f"{prefix}node: {info[1]}")
        else:
            message.append(f"{prefix}stdout: none")
        if self.paths.stderr.exists():
            message.append(f"<{prefix}stderr: {self.paths.stderr}")
        else:
            message.append(f"{prefix}stderr: none")
        return "\n".join(message)

    def __repr__(self):
        return f"{self.__class__.__name__}<job_id={self.job_id}>"
