##########################################################################
# Hopla - Copyright (C) AGrigis, 2015 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
This module contains a 'hopla' function used to create a list of commands
that will be executed in parallel using the local machine or cluster with
TORQUE resource manager installed. For the moment, the input script must be
a Python script.
"""  # pragma: no cover

# System import
import os  # pragma: no cover
from collections import OrderedDict  # pragma: no cover

# Hopla import
from .scheduler import scheduler  # pragma: no cover


def hopla(python_script, hopla_outputdir=None, hopla_cpus=1,
          hopla_use_subprocess=False, hopla_delay_upto=0, hopla_optional=None,
          hopla_logfile=None, hopla_verbose=1, hopla_cluster=False,
          hopla_cluster_logdir=None, hopla_cluster_queue=None,
          hopla_cluster_memory=1, hopla_cluster_walltime=72,
          hopla_cluster_nb_threads=1, hopla_cluster_python_cmd="python",
          hopla_iterative_kwargs=None, **kwargs):
    """ Execute a python script/file in parallel.

    Rules:

        * This procedure enables local or cluster runs.
        * This procedure returns a human readable log.
        * In the command line, prefix kwargs with a '-' if name not in
          'hopla_optional' list, otherwise with a '--'.
        * In order not to interfer with command line kwargs use 'hopla' prefix
          in function parameters.
        * If the script contains a '__hopla__' list of parameter names to keep
          trace on, all the specified parameters values are stored in the
          execution status.

    Parameters
    ----------
    python_script: str (mandatory)
        a python script or file to be executed.
    hopla_outputdir: str (optional, default None)
        a folder where synthetic results are written.
    hopla_cpus: int (optional, default 1)
        the number of cpus to be used.
    hopla_use_subprocess: bool, default False
        use a subprocess (for instance in case of memory leak). In this
        particular case the __hopla__ setting is deactivated.
    hopla_delay_upto: int (optional, default 0)
        the processes' execution will be delayed randomly by [0, <delay_upto>[
        seconds.
    hopla_optional: list of str (optional, default None)
        the optional kwagrs names that will be prefixed with '--' in the
        command line.
    hopla_logfile: str (optional, default None)
        location where the log messages are redirected: INFO and DEBUG.
    hopla_verbose: int (optional, default 1)
        0 - display no log in console,
        1 - display information log in console,
        2 - display debug log in console.
    hopla_cluster: bool (optional, default False)
        if True use a worker that submits the jobs to a cluster.
    hopla_cluster_logdir: str (optional, default None)
        an existing path where the cluster error and output files will be
        stored. This folder must be empty.
    hopla_cluster_queue: str (optional, default None)
        the name of the queue where the jobs will be submited.
    hopla_cluster_memory: float (optional, default 1)
        the memory allocated to each job submitted on a cluster (in GB).
    hopla_cluster_walltime: int (optional, default 72)
        the walltime used for each job submitted on the cluster (in hours).
    hopla_cluster_nb_threads: int (optional, default 1)
        the number of cores allocated for each node.
    hopla_cluster_python_cmd: str (optional, default 'python')
        the path to the python binary.
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
    # Function parameters
    hopla_optional = hopla_optional or []

    # Create the commands to be executed by the scheduler
    iterative_kwargs = hopla_iterative_kwargs or []
    commands = []
    values_count = []
    # > sort kwargs
    kwargs = OrderedDict(sorted(list(kwargs.items())))
    # > deal kwargs with iterative kwargs
    for name, values in kwargs.items():
        if name in iterative_kwargs:
            if not isinstance(values, list):
                raise ValueError(
                    "All the iterative kwargs must be of list type. Parameter "
                    "'{0}' with value '{1}' does not fulfill this "
                    "rule.".format(name, values))
            values_count.append(len(values))
            for index, val in enumerate(values):
                if len(commands) <= index:
                    commands.append([])
                if val is None:
                    continue
                # > in the command line, prefix kwargs with '-',
                # optional kwargs with '--'
                if name in hopla_optional:
                    option = ["--" + name]
                else:
                    option = ["-" + name]
                # > set the option value
                if isinstance(val, list):
                    option.extend([str(item) for item in val])
                elif not isinstance(val, bool):
                    option.append(str(val))
                # > set the option in the command line: for boolean set the
                # option only if the value is true
                if isinstance(val, bool):
                    if val:
                        commands[index].extend(option)
                else:
                    commands[index].extend(option)
    # > check iterative kwargs values have the same length
    if (values_count != [] and
            values_count.count(values_count[0]) != len(values_count)):
        raise ValueError("All the iterative kwargs must have the "
                         "same number of values in order to iterate.")
    # > add script name to command line and deal with non iterative kwargs
    for cmd in commands:
        cmd.insert(0, python_script)
        for name, value in kwargs.items():
            if name not in iterative_kwargs:
                # > skip None value
                if value is None:
                    continue
                # > in the command line, prefix kwargs with '-',
                # optional kwargs with '--'
                if name in hopla_optional:
                    option = ["--" + name]
                else:
                    option = ["-" + name]
                # > set the option value
                if isinstance(value, list):
                    option.extend([str(item) for item in value])
                elif not isinstance(value, bool):
                    option.append(str(value))
                # > set the option in the command line: for boolean set the
                # option only if the value is true
                if isinstance(value, bool):
                    if value:
                        cmd.extend(option)
                else:
                    cmd.extend(option)

    # Execute the commands with a scheduler in order to control the execution
    # load
    script_name = python_script.split(os.sep)[-1].split(".")[0]
    return scheduler(commands=commands,
                     name=script_name,
                     outputdir=hopla_outputdir,
                     cpus=hopla_cpus,
                     use_subprocess=hopla_use_subprocess,
                     delay_upto=hopla_delay_upto,
                     logfile=hopla_logfile,
                     cluster=hopla_cluster,
                     cluster_logdir=hopla_cluster_logdir,
                     cluster_queue=hopla_cluster_queue,
                     cluster_memory=hopla_cluster_memory,
                     cluster_walltime=hopla_cluster_walltime,
                     cluster_nb_threads=hopla_cluster_nb_threads,
                     cluster_python_cmd=hopla_cluster_python_cmd,
                     verbose=hopla_verbose)
