##########################################################################
# Hopla - Copyright (C) AGrigis, 2015 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
This module proposes a local worker and a distant TORQUE worker. The two
proposed workers are able to follow a '__hopla__' list of parameter
names to keep trace on. All specified parameters values are stored in the
execution status.
"""

# System import
import os
import copy
import subprocess
import traceback
from socket import getfqdn
import sys
import glob
import time
import json

# Hopla import
from .signals import FLAG_ALL_DONE
from .signals import FLAG_WORKER_FINISHED_PROCESSING


def worker(tasks, returncodes):
    """ The worker function for a script.

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


PBS_TEMPLATE = """
#!/bin/bash
#PBS -l mem={memory}gb,nodes=1:ppn=1,walltime={hwalltime}:00:00
#PBS -N {name}
#PBS -e {errfile}
#PBS -o {logfile}
{command}
"""


PY_TEMPLATE = """
from __future__ import print_function
import sys
import json


# Execute the command line in the 'job_status' environment
command = {cmd}
sys.argv = command
job_status = dict()
parameters = dict()
with open(command[0]) as ofile:
    exec(ofile.read(), job_status)

# Check for the parameters to keep trace on (the parameters specified in the
# '__hopla__' cariable
if "__hopla__" in job_status:
    for parameter_name in job_status["__hopla__"]:
        if parameter_name in job_status:
            parameters[parameter_name] = job_status[parameter_name]

# Print the parameters to keep trace on in order to communicate with the
# scheduler and in order to generate a complete log
print("<hopla>")
print(parameters)
print("</hopla>")
"""


def qsub_worker(tasks, returncodes, logdir, queue,
                memory=1, walltime=24, python_cmd="python", sleep=2):
    """ A cluster worker function for a script.

    Use the TORQUE resource manager provides control over batch jobs and
    distributed computing resources. It is an advanced open-source product
    based on the original PBS project.

    Use a double script strategy in order to manage the '__hopla__' list of
    parameter names to keep trace on: a '.pbs' script calling another '.py'
    script that print the '__hopla__' parameters. All the specified parameters
    values are stored in the return code.

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
    walltime: int (optional, default 24)
        the walltime used for each job submitted on the cluster (in hours).
    python_cmd: str (optional, default 'python')
        the path to the python binary.
    sleep: float (optional, default 2)
        time rate to check the termination of the submited jobs.
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

        # COMPATIBILITY: dict in python 2 becomes structure in python 3
        python_version = sys.version_info
        if python_version[0] < 3:
            environ = copy.deepcopy(os.environ.__dict__)
        else:
            environ = copy.deepcopy(os.environ._data)
        returncode[job_name]["debug"]["environ"] = environ

        # Torque-PBS execution
        fname_pbs = os.path.join(logdir, job_name + ".pbs")
        fname_py = os.path.join(logdir, job_name + ".py")
        pbs_cmd = " ".join([python_cmd, fname_py])
        errfile = os.path.join(logdir, "error." + job_name)
        logfile = os.path.join(logdir, "output." + job_name)
        try:
            # Edit the job to be submitted
            with open(fname_py, "w") as open_file:
                open_file.write(PY_TEMPLATE.format(cmd=command))
            with open(fname_pbs, "w") as open_file:
                open_file.write(PBS_TEMPLATE.format(
                    memory=memory, hwalltime=walltime, name=job_name,
                    errfile=errfile + ".$PBS_JOBID",
                    logfile=logfile + ".$PBS_JOBID", command=pbs_cmd))

            # Submit the job
            subprocess.check_call(["qsub", "-q", queue, fname_pbs])

            # Lock everything until the submitted command has not terminated
            while True:
                terminated = len(glob.glob(errfile + ".*")) > 0
                if terminated:
                    break
                time.sleep(sleep)

            # Check that no error was produced during the submission
            with open(glob.glob(errfile + ".*")[0]) as open_file:
                stderr = open_file.readlines()
            if len(stderr) > 0:
                raise Exception("\n".join(stderr))

            # Get the 'hopla' parameters to keep trace on
            with open(glob.glob(logfile + ".*")[0]) as open_file:
                stdout = open_file.read()
            hopla_start = stdout.rfind("<hopla>")
            hopla_end = stdout.rfind("</hopla>")
            parameters_repr = stdout[hopla_start + len("<hopla>"): hopla_end]
            parameters = json.loads(
                parameters_repr.strip("\n").replace("'", '"'))

            # Get the 'hopla' parameters to keep trace on
            with open(glob.glob(logfile + ".*")[0]) as open_file:
                stdout = open_file.read()
            hopla_start = stdout.rfind("<hopla>")
            hopla_end = stdout.rfind("</hopla>")
            parameters_repr = stdout[hopla_start + len("<hopla>"): hopla_end]
            parameters = json.loads(
                parameters_repr.strip("\n").replace("'", '"'))

            # Update the return code
            for name, value in parameters.items():
                returncode[job_name]["info"][name] = value
            returncode[job_name]["info"]["exitcode"] = "0"
        # Error
        except:
            if os.path.isfile(errfile):
                with open(errfile) as openfile:
                    error_message = openfile.readlines()
            else:
                error_message = traceback.format_exc()
            returncode[job_name]["info"]["exitcode"] = (
                "1 - '{0}'".format(error_message))
        returncodes.put(returncode)
