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
import logging
import json
import multiprocessing

# Hopla import
import hopla
from .workers import worker
from .workers import qsub_worker
from .signals import FLAG_ALL_DONE
from .signals import FLAG_WORKER_FINISHED_PROCESSING

# Define the logger for this file
multiprocessing.log_to_stderr(logging.CRITICAL)
logger = logging.getLogger("hopla")


def scheduler(commands, outputdir=None, cpus=1, logfile=None, cluster=False,
              cluster_logdir=None, cluster_queue=None, cluster_memory=1,
              cluster_python_cmd="python", verbose=1):
    """ Execute some commands (python scripts) using a scheduler.

    If the script contains a '__hopla__' list of parameter names to keep
    trace on, all the specified parameters values are stored in the execution
    status.

    Parameters
    ----------
    commands: list of list of str (mandatory)
        some commands to be executed: the first command element must be a
        path to a python script.
    outputdir: str (optional, default None)
        a folder where a summary of the executed jobs are written.
    cpus: int (optional, default 1)
        the number of cpus to be used.
    logfile: str (optional, default None)
        location where the log messages are redirected: INFO and DEBUG.
    cluster: bool (optional, default False)
        if True use a worker that submits the jobs to a cluster.
    cluster_logdir: str (optional, default None)
        an existing path where the cluster error and output files will be
        stored. This folder must be empty.
    cluster_queue: str (optional, default None)
        the name of the queue where the jobs will be submited.
    cluster_memory: float (optional, default 1)
        the memory allocated to each job submitted on a cluster (in GB).
    cluster_python_cmd: str (optional, default 'python')
        the path to the python binary.
    verbose: int (optional, default 1)
        0 - display no log in console,
        1 - display information log in console,
        2 - display debug log in console.

    Returns
    -------
    execution_status: dict
        a dictionary that contains all the executed command return codes.
    exitcodes: dict
        a dictionary with a summary of the executed jobs exit codes.
    """
    # If someone tried to log something before basicConfig is called,
    # Python creates a default handler that goes to the console and
    # will ignore further basicConfig calls: we need to remove the
    # handlers if there is one.
    while len(logging.root.handlers) > 0:
        logging.root.removeHandler(logging.root.handlers[-1])

    # Remove console and file handlers if already created
    while len(logger.handlers) > 0:
        logger.removeHandler(logger.handlers[-1])

    # Create console handler.
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    if verbose != 0:
        console_handler = logging.StreamHandler()
        if verbose == 1:
            logger.setLevel(logging.INFO)
            console_handler.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)
            console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    else:
        logger.addHandler(logging.NullHandler())

    # Create a file handler if requested
    if logfile is not None:
        file_handler = logging.FileHandler(logfile, mode="a")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
        logger.info("Processing information will be logged in file "
                    "'{0}'.".format(logfile))

    # Information
    logger.info("Using 'hopla' version '{0}'.".format(hopla.__version__))
    exit_rules = [
        "For exitcode values:",
        "    = 0 - no error was produced.",
        "    > 0 - the process had an error, and exited with that code.",
        "    < 0 - the process was killed with a signal of -1 * exitcode."]
    logger.info("\n".join(exit_rules))

    # Get the machine available cpus
    nb_cpus = multiprocessing.cpu_count() - 1
    nb_cpus = nb_cpus or 1
    if max(cpus, nb_cpus) == cpus:
        cpus = nb_cpus

    # Create the workers
    # Works as a FIFO with 1 cpu
    workers = []
    tasks = multiprocessing.Queue()
    returncodes = multiprocessing.Queue()
    for index in range(cpus):
        if cluster:
            if not os.path.isdir(cluster_logdir):
                raise ValueError(
                    "'{0}' is not a valid directory.".format(cluster_logdir))
            if len(os.listdir(cluster_logdir)) > 0:
                raise ValueError(
                    "'{0}' is not an empty directory.".format(cluster_logdir))
            if cluster_queue is None:
                raise ValueError(
                    "In order to execute the jobs on the cluster, please "
                    "specify an execution queue.")
            process = multiprocessing.Process(
                target=qsub_worker, args=(tasks, returncodes, cluster_logdir,
                                          cluster_queue, cluster_memory,
                                          cluster_python_cmd))
        else:
            process = multiprocessing.Process(
                target=worker, args=(tasks, returncodes))
        process.deamon = True
        process.start()
        workers.append(process)

    # Execute the input commands
    # Use a FIFO strategy to deal with multiple boxes
    execution_status = {}
    workers_finished = 0
    try:
        # Assert something has to be executed
        if len(commands) == 0:
            raise Exception("Nothing to execute.")

        # Add all the jobs to the 'tasks' queue
        for cnt, cmd in enumerate(commands):
            job_name = "job_{0}".format(cnt)
            tasks.put((job_name, cmd))

        # Add poison pills to stop the remote workers
        for index in range(cpus):
            tasks.put(FLAG_ALL_DONE)

        # Loop until all the jobs are finished
        while True:

            # Collect the box returncodes
            wave_returncode = returncodes.get()
            if wave_returncode == FLAG_WORKER_FINISHED_PROCESSING:
                workers_finished += 1
                if workers_finished == cpus:
                    break
                continue
            job_name = list(wave_returncode.keys())[0]
            execution_status.update(wave_returncode)

            # Information
            for key, value in wave_returncode[job_name]["info"].items():
                logger.info("{0}.{1} = {2}".format(
                    job_name, key, value))
            for key, value in wave_returncode[job_name]["debug"].items():
                logger.debug("{0}.{1} = {2}".format(
                    job_name, key, value))
    except:
        # Stop properly all the workers before raising the exception
        for process in workers:
            process.terminate()
            process.join()
        raise

    # Save processing status to ease the generated data interpretation if the
    # 'outputdir' is not None
    exitcodes = {}
    for job_name, job_returncode in execution_status.items():
        exitcodes[job_name] = int(job_returncode["info"]["exitcode"].split(
            " - ")[0])
    if outputdir is not None:
        exitcodes_file = os.path.join(outputdir, "scheduler_status.json")
        with open(exitcodes_file, "w") as open_file:
            json.dump(exitcodes, open_file, indent=4, sort_keys=True)

    return execution_status, exitcodes
