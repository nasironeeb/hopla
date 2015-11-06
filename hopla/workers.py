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
import subprocess
import traceback
from socket import getfqdn
import sys
import glob
import time

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


def qsub_worker(tasks, returncodes, logdir, queue,
                memory=1, python_cmd="python", sleep=2):
    """ A cluster worker function of a script.

    Parameters
    ----------
    tasks, returncodes: multiprocessing.Queue
        the input (commands) and output (results) queues.
    logdir: str
        a path where the qsub error and output files will be stored.
    queue: str
        the name of the queue where the jobs will be submited.
    memory: float (optional, default 1)
        the memory allocated to each qsub (in GB).
    python_cmd: str (optional, default 'python')
        the path to the python binary.
    sleep: float (optional, default 2)
        time rate to check the termination of the submited jobs.
    """

    TEMPLATE = """
    #!/bin/bash
    #PBS -l mem={memory}gb,nodes=1:ppn=1,walltime=24:00:00
    #PBS -N {name}
    #PBS -e {errfile}
    #PBS -o {logfile}
    {command}
    """

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
        fname = os.path.join(logdir, job_name + ".pbs")
        cmd = " ".join([python_cmd] + command)
        errfile = os.path.join(logdir, "error." + job_name)
        logfile = os.path.join(logdir, "output." + job_name)
        try:
            with open(fname, "w") as submit:
                submit.write(TEMPLATE.format(
                    memory=memory, name=job_name,
                    errfile=errfile + ".$PBS_JOBID",
                    logfile=logfile + ".$PBS_JOBID", command=cmd))
            subprocess.check_call(["qsub", "-q", queue, fname])

            # Lock everything until the qsub command has not terminated
            while True:
                terminated = len(glob.glob(errfile + ".*")) > 0
                if terminated:
                    break
                time.sleep(sleep)

            returncode[job_name]["info"]["exitcode"] = "0"
        # Error
        except:
            with open(errfile) as openfile:
                error_message = openfile.readlines()
            returncode[job_name]["info"]["exitcode"] = (
                "1 - '{0}'".format(error_message))
        finally:
            pass

        returncodes.put(returncode)
