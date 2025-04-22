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

import copy
import json
import os
import subprocess
from pathlib import Path

from .utils import DelayedJob, InfoWatcher


class CCCInfoWatcher(InfoWatcher):
    """ An instance of this class is shared by all jobs, and is in charge of
    calling ccc to check status for all jobs at once.

    Parameters
    ----------
    delay_s: int, default 60
        maximum delay before each non-forced call to the cluster.
    """
    def __init__(self, delay_s=60):
        super().__init__(delay_s)

    @property
    def update_command(self):
        """ Return the command to list jobs status.
        """
        active_jobs = self._registered - self._finished
        return "squeue --states=all --json -j " + ",".join(active_jobs)

    @property
    def valid_status(self):
        """ Return the list of valid status.
        """
        return ["RUNNING", "PENDING", "SUSPENDED", "COMPLETING", "CONFIGURING",
                "UNKNOWN"]

    @classmethod
    def read_info(cls, string):
        """ Reads the output of squeue and returns a dictionary containing
        main jobs information.
        """
        if not isinstance(string, str):
            string = string.decode()
        all_stats = {str(val["job_id"]): val
                     for val in json.loads(string)["jobs"]}
        return all_stats


class DelayedCCCJob(DelayedJob):
    """ Represents a job that have been queue for submission by an executor,
    but hasn't yet been scheduled.

    Parameters
    ----------
    delayed_submission: DelayedSubmission
        a delayed submission allowing to generate the command line to
        execute.
    executor: Executor
        base job executor.
    job_id: str
        the job identifier.
    """
    _hub = "n4h00001rs"
    _submission_cmd = "ccc_msub"

    def __init__(self, delayed_submission, executor, job_id):
        super().__init__(delayed_submission, executor, job_id)
        path = Path(__file__).parent / "ccc_batch_template.txt"
        with open(path) as of:
            self.template = of.read()
        image = self._executor.parameters["image"]
        assert image is not None, "Please select or give an image."
        if os.path.isfile(image):
            self.image_file = image
            self.image_name = os.path.basename(image).split(".")[0]
        else:
            self.image_file = None
            self.image_name = image

    def generate_batch(self):
        """ Write the batch file.
        """
        params = copy.deepcopy(self._executor.parameters)
        params["walltime"] *= 3600
        params["memory"] *= 1000
        self.import_image()
        cmd = (f"pcocc-rs run {self._hub}:{self.image_name} "
               f"{self.delayed_submission.command}")
        with open(self.paths.submission_file, "w") as of:
            if self.paths.stdout.exists():
                os.remove(self.paths.stdout)
            if self.paths.stderr.exists():
                os.remove(self.paths.stderr)
            of.write(self.template.format(
                command=cmd,
                stdout=self.paths.stdout,
                stderr=self.paths.stderr,
                **params))

    def import_image(self):
        """ Load the docker image if not available.
        """
        cmd = ["pcocc-rs", "image", "list", "-r", self._hub]
        stdout = subprocess.check_output(cmd)
        if self.image_name not in self.read_index(stdout):
            if self.image_file is None:
                raise ValueError(
                    f"'{self.image_name}' image not available! Please "
                    "consider providing the image archive.")
            cmd = [
                "pcocc-rs", "image", "import",
                f"docker-archive:{self.image_file}",
                f"{self._hub}:{self.image_name}"]
            subprocess.check_call(cmd)

    @classmethod
    def read_index(cls, string):
        """ Reads the output of of pcocc-rs image list and returns a
        list available container.
        """
        if not isinstance(string, str):
            string = string.decode()
        names = [item.strip().split(" ")[0]
                 for item in string.split("\n")[2:-2]]
        return names

    def read_jobid(self, string):
        """ Return the started job ID.
        """
        if not isinstance(string, str):
            string = string.decode()
        return string.rstrip("\n").strip().split(" ")[-1]

    @property
    def start_command(self):
        """ Return the start job command.
        """
        return type(self)._submission_cmd

    @property
    def stop_command(self):
        """ Return the stop job command.
        """
        return "ccc_mqdel"

    def __repr__(self):
        return (f"{self.__class__.__name__}<job_id={self.job_id},"
                f"submission_id={self.submission_id},image={self._hub}:"
                f"{self.image_name}>")
