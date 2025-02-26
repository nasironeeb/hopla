##########################################################################
# Hopla - Copyright (C) AGrigis, 2015 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Contains some utility functions.
"""

import shutil


class JobPaths:
    """ Creates paths related to a job and its submission.

    Parameters
    ----------
    folder: Path
        the current execution folder.
    job_id: str
        the job identifier.
    """
    def __init__(self, folder, job_id):
        self.submission_folder = folder / "submissions"
        self.log_folder = folder / "logs"
        if self.submission_folder.exists():
            shutil.rmtree(self.submission_folder)
        if self.log_folder.exists():
            shutil.rmtree(self.log_folder)
        self.submission_folder.mkdir(parents=True, exist_ok=True)
        self.log_folder.mkdir(parents=True, exist_ok=True)
        self.job_id = job_id

    @property
    def submission_file(self):
        """ Generate the submission file location.
        """
        return self.submission_folder / f"{self.job_id}_submission.sh"

    @property
    def stderr(self):
        """ Generate the stderr file location.
        """
        return self.log_folder / f"{self.job_id}_log.err"

    @property
    def stdout(self):
        """ Generate the stdout file location.
        """
        return self.log_folder / f"{self.job_id}_log.out"
