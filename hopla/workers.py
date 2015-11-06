#! /usr/bin/env python
##########################################################################
# Hopla - Copyright (C) AGrigis, 2015
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import os
import copy

# Hopla import
from .signals import FLAG_ALL_DONE
from .signals import FLAG_WORKER_FINISHED_PROCESSING


def worker(tasks, returncodes):
    """ The worker function of a script.

    If the script contains a '__hopla__' list of parameter names to keep
    trace on, all the specified parameters values are stored in the return
    code.

    Parameters
    ----------
    tasks, returncodes: multiprocessing.Queue
        the input (commands) and output (results) queues.
    """
    import traceback
    from socket import getfqdn
    import sys

    while True:
        signal = tasks.get()
        if signal == FLAG_ALL_DONE:
            returncodes.put(FLAG_WORKER_FINISHED_PROCESSING)
            break
        job_name, command = signal
        returncode = {}
        returncode[job_name] = {}
        returncode[job_name]["info"] = {}
        returncode[job_name]["debug"] = {}
        returncode[job_name]["info"]["cmd"] = command
        returncode[job_name]["debug"]["hostname"] = getfqdn()

        # COMPATIBILITY: dict in python 2 becomes structure in pyton 3
        python_version = sys.version_info
        if python_version[0] < 3:
            environ = copy.deepcopy(os.environ.__dict__)
        else:
            environ = copy.deepcopy(os.environ._data)
        returncode[job_name]["debug"]["environ"] = environ

        # Execution
        try:
            sys.argv = command
            job_status = {}
            with open(command[0]) as ofile:
                exec(ofile.read(), job_status)
            if "__hopla__" in job_status:
                for parameter_name in job_status["__hopla__"]:
                    if parameter_name in job_status:
                        returncode[job_name]["info"][
                            parameter_name] = job_status[parameter_name]
            returncode[job_name]["info"]["exitcode"] = "0"
        # Error
        except:
            returncode[job_name]["info"]["exitcode"] = (
                "1 - '{0}'".format(traceback.format_exc()))
        returncodes.put(returncode)
