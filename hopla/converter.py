#! /usr/bin/env python
##########################################################################
# Hopla - Copyright (C) AGrigis, 2015
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# Hopla import
from .scheduler import scheduler


def hopla(python_script, hopla_outputdir=None, hopla_cpus=1,
          hopla_logfile=None, hopla_verbose=1, hopla_cluster=False,
          hopla_cluster_logdir=None, hopla_cluster_queue=None,
          hopla_cluster_memory=1, hopla_cluster_python_cmd="python",
          hopla_iterative_kwargs=None, **kwargs):
    """ Execute a Python script in parallel.

    Rules:

        * This procedure enables local or cluster runs.
        * This procedure returns a human readable log.
        * Prefix all kwargs with one character with a '-', the other with
          a '--'.
        * In order not to interfer with command line kwargs use 'hopla' prefix
          in function parameters.

    Parameters
    ----------
    python_script: str (mandatory)
        a path to a file containin a Python script to be executed.
    hopla_outputdir: str (optional, default None)
        a folder where synthetic results are written.
    hopla_cpus: int (optional, default 1)
        the number of cpus to be used.
    hopla_logfile: str (optional, default None)
        location where the log messages are redirected: INFO and DEBUG.
    hopla_cluster: bool (optional, default False)
        if True use a worker that submits the jobs to a cluster.
    hopla_cluster_logdir: str (optional, default None)
        an existing path where the cluster error and output files will be
        stored. This folder must be empty.
    hopla_cluster_queue: str (optional, default None)
        the name of the queue where the jobs will be submited.
    hopla_cluster_memory: float (optional, default 1)
        the memory allocated to each job submitted on a cluster (in GB).
	hopla_cluster_python_cmd: str (optional, default 'python')
        the path to the python binary.
    hopla_verbose: int (optional, default 1)
        0 - display no log in console,
        1 - display information log in console,
        2 - display debug log in console.
    hopla_iterative_kwargs: list of str (optional, default None)
        the iterative script parameters.
    kwargs: dict (optional)
        the script parameters: iterative kwargs must contain a list of elements
        and must all have the same length, non-iterative kwargs will be
        replicated.

    Returns
    -------
    execution_status: dict
        a dictionary that contains all the executed command return codes.
    exitcodes: dict
        a dictionary with a summary of the executed jobs exit codes.
    """
    # Create the commands to be executed by a scheduler
    iterative_kwargs = hopla_iterative_kwargs or []
    commands = []
    values_count = []
    for name, values in kwargs.items():
        if name in iterative_kwargs:
            if not isinstance(values, list):
                raise ValueError(
                    "All the iterative kwargs must be of list type. Parameter "
                    "'{0}' with value '{1}' does not fulfill this "
                    "rule.".format(name, values))
            if len(name) > 1:
                option = "--" + name
            else:
                option = "-" + name
            values_count.append(len(values))
            for index, val in enumerate(values):
                if len(commands) <= index:
                    commands.append([])
                commands[index].append(option)
                if not isinstance(val, bool):
                    commands[index].append(str(val))
    if (values_count != [] and
            values_count.count(values_count[0]) != len(values_count)):
        raise ValueError("All the iterative kwars values must have the "
                         "same number of values in order to iterate.")
    for cmd in commands:
        cmd.insert(0, python_script)
        for name, value in kwargs.items():
            if name not in iterative_kwargs:
                if len(name) > 1:
                    option = "--" + name
                else:
                    option = "-" + name
                cmd.append(option)
                if not isinstance(value, bool):
                    cmd.append(str(value))

    # Execute the commands with a scheduler
    return scheduler(commands, hopla_outputdir, hopla_cpus, hopla_logfile,
                     hopla_cluster, hopla_cluster_logdir, hopla_cluster_queue,
                     hopla_cluster_memory, hopla_cluster_python_cmd,
                     hopla_verbose)
