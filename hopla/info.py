#! /usr/bin/env python
##########################################################################
# Hopla - Copyright (C) AGrigis, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# pragma: no cover

# Pysphinxdoc current version
version_major = 1  # pragma: no cover
version_minor = 0  # pragma: no cover
version_micro = 2  # pragma: no cover

# Expected by setup.py: string of form "X.Y.Z"
__version__ = "{0}.{1}.{2}".format(
    version_major, version_minor, version_micro)  # pragma: no cover

# Project descriptions
DESCRIPTION = "[hopla] Easy to use pure-Python scheduler."  # pragma: no cover
LONG_DESCRIPTION = """
Easy to use pure-Python scheduler.

Overview
========

With the increasing amount of data to be treated, efficient scaling strategies
are necessary. This observation made me start 'hopla' which provides:

- a scheduler that produces human readable outputs.
- a converter that enables to execute kilometer command lines
- workers that enable local or cluster executions.


Usage
=====

The proposed module has been currently developped to execute Python scripts.
Consider the following demonstration script that lists an input folder (the
latter is available in the 'hopla.demo.my_ls_script' module)::

    #! /usr/bin/env python
    ##########################################################################
    # Hopla - Copyright (C) AGrigis, 2015
    # Distributed under the terms of the CeCILL-B license, as published by
    # the CEA-CNRS-INRIA. Refer to the LICENSE file or to
    # http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
    # for details.
    ##########################################################################

    # Bredala import
    try:
        import bredala
        bredala.USE_PROFILER = False
        bredala.register("os.path", names=["listdir"])
    except:
        pass

    # System import
    from datetime import datetime
    import argparse
    import os

    # Parameters to keep trace
    __hopla__ = ["runtime", "inputs", "outputs"]


    def is_directory(dirarg):
        if not os.path.isdir(dirarg):
            raise argparse.ArgumentError(
                "The directory '{0}' does not exist!".format(dirarg))
        return dirarg


    parser = argparse.ArgumentParser(description="List a directory.")
    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "-d", "--dir", dest="dir", required=True, metavar="PATH",
        help="a valid directory to be listed.", type=is_directory)
    parser.add_argument(
        "-b", "--fbreak", dest="fbreak", action="store_true",
        help="a activated raise a ValueError.")
    required.add_argument(
        "-l", "--mylist", dest="mylist", nargs="+", type=int, required=True,
        help="a list that will be printed.")
    parser.add_argument(
        "-v", "--verbose", dest="verbose", type=int, choices=[0, 1, 2], default=0,
        help="increase the verbosity level: 0 silent, [1, 2] verbose.")
    args = parser.parse_args()

    directory = args.dir
    break_flag = args.fbreak
    mylist = args.mylist
    runtime = {
        "timestamp": datetime.now().isoformat()
    }
    inputs = {
        "directory": directory,
        "break_flag": break_flag,
        "mylist": mylist
    }
    outputs = None
    if break_flag:
        raise ValueError("BREAK ACTIVATED.")
    files = os.listdir(directory)
    print("[res] --------", mylist)
    if args.verbose > 0:
        print("[res] --------", files)
    outputs = {
        "files": files
    }

Note the '__hopla__' list that specifies which parameters will be dispalyed in
the scheduler execution log. This mechanism is usefull to keep trace of
important script elements. The scaled execution of this script on two CPUs is
realized using a simple call::

    # System import
    from pprint import pprint

    # Hopla import
    from hopla.converter import hopla
    import hopla as root

    # Define script parameters
    apath = os.path.join(os.path.abspath(os.path.dirname(root.__file__)), "demo")
    script = os.path.join(apath, "my_ls_script.py")

    # Local execution
    status, exitcodes = hopla(
        script, hopla_iterative_kwargs=["d", "b"], verbose=0, l=[1, 2],
        b=[False, True, False], d=[apath, apath, apath], hopla_verbose=1,
        hopla_cpus=2)
    pprint(status)
    pprint(exitcodes)

After the execution call (through the hopla function), exit codes are
inspected. The 'hopla_verbose' has been set to one, some logging information
has been displayed::

    2016-08-02 15:59:26,562 - INFO - Using 'hopla' version '1.0.2'.
    2016-08-02 15:59:26,562 - INFO - For exitcode values:
        = 0 - no error was produced.
        > 0 - the process had an error, and exited with that code.
        < 0 - the process was killed with a signal of -1 * exitcode.
    2016-08-02 15:59:26,927 - INFO - job_0.inputs = {'directory': '/home/ag239446/git/hopla/hopla/demo', 'break_flag': False, 'mylist': [1, 2]}
    2016-08-02 15:59:26,928 - INFO - job_0.exitcode = 0
    2016-08-02 15:59:26,928 - INFO - job_0.cmd = ['/home/ag239446/git/hopla/hopla/demo/my_ls_script.py', '--dir', '/home/ag239446/git/hopla/hopla/demo', '--mylist', '1', '2', '--verbose', '1']
    2016-08-02 15:59:26,928 - INFO - job_0.outputs = {'files': ['my_ls_script.py', 'demo.py']}
    2016-08-02 15:59:26,928 - INFO - job_0.runtime = {'timestamp': '2016-08-02T15:59:26.926153'}
    2016-08-02 15:59:26,928 - INFO - job_1.inputs = {'directory': '/home/ag239446/git/hopla/hopla/demo', 'break_flag': True, 'mylist': [1, 2]}
    2016-08-02 15:59:26,929 - INFO - job_1.exitcode = 1 - 'Traceback (most recent call last):
      File "/home/ag239446/git/hopla/hopla/workers.py", line 70, in worker
        exec(ofile.read(), job_status)
      File "<string>", line 65, in <module>
    ValueError: BREAK ACTIVATED.
    '
    2016-08-02 15:59:26,929 - INFO - job_1.cmd = ['/home/ag239446/git/hopla/hopla/demo/my_ls_script.py', '-b', '--dir', '/home/ag239446/git/hopla/hopla/demo', '--mylist', '1', '2', '--verbose', '1']
    2016-08-02 15:59:26,929 - INFO - job_1.outputs = None
    2016-08-02 15:59:26,929 - INFO - job_1.runtime = {'timestamp': '2016-08-02T15:59:26.926772'}
    2016-08-02 15:59:26,979 - INFO - job_2.inputs = {'directory': '/home/ag239446/git/hopla/hopla/demo', 'break_flag': False, 'mylist': [1, 2]}
    2016-08-02 15:59:26,979 - INFO - job_2.exitcode = 0
    2016-08-02 15:59:26,979 - INFO - job_2.cmd = ['/home/ag239446/git/hopla/hopla/demo/my_ls_script.py', '--dir', '/home/ag239446/git/hopla/hopla/demo', '--mylist', '1', '2', '--verbose', '1']
    2016-08-02 15:59:26,979 - INFO - job_2.outputs = {'files': ['my_ls_script.py', 'demo.py']}
    2016-08-02 15:59:26,979 - INFO - job_2.runtime = {'timestamp': '2016-08-02T15:59:26.969334'}
    {'job_0': 0, 'job_1': 1, 'job_2': 0}


Perspectives
============

It will be nice to generalize some concepts (ie., accept different kind
of scripts).
"""  # pragma: no cover

# Main setup parameters
NAME = "hopla"  # pragma: no cover
AUTHOR = "Antoine Grigis"  # pragma: no cover
AUTHOR_EMAIL = "antoine.grigis@cea.fr"  # pragma: no cover
URL = "https://github.com/AGrigis/hopla"  # pragma: no cover
DOWNLOAD_URL = "https://github.com/AGrigis/hopla"  # pragma: no cover
LICENSE = "GPL 2+"  # pragma: no cover
VERSION = __version__  # pragma: no cover
