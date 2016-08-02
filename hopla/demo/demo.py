#! /usr/bin/env python
##########################################################################
# Hopla - Copyright (C) AGrigis, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import os
from pprint import pprint

# Hopla import
import hopla as root
from hopla.converter import hopla


# Define script parameters
apath = os.path.join(os.path.abspath(os.path.dirname(root.__file__)), "demo")
script = os.path.join(apath, "my_ls_script.py")
cluster_logdir = os.path.join(apath, "pbs_logs")

# Local execution
status, exitcodes = hopla(
    script, d=[apath, apath, apath], b=False, v=1, l=[1, 2],
    hopla_iterative_kwargs=["d"], hopla_verbose=1, hopla_cpus=10)
pprint(exitcodes)

# Local execution with optional arguments
status, exitcodes = hopla(
    script, dir=[apath, apath, apath], b=False, verbose=1, mylist=[1, 2],
    hopla_iterative_kwargs=["dir"], hopla_verbose=1, hopla_cpus=10,
    hopla_optional=["dir", "verbose", "mylist"])
pprint(exitcodes)

# Local execution with boolean iter
status, exitcodes = hopla(
    script, dir=[apath, apath, apath], b=[False, True, False], verbose=1,
    mylist=[1, 2],
    hopla_iterative_kwargs=["dir", "b"], hopla_verbose=1, hopla_cpus=10,
    hopla_optional=["dir", "verbose", "mylist"])
pprint(exitcodes)

# Local execution with list iter
status, exitcodes = hopla(
    script, dir=[apath, apath, apath], b=False, verbose=1,
    mylist=[[1, 2], [2, 3], [3, 4]],
    hopla_iterative_kwargs=["dir", "mylist"], hopla_verbose=1, hopla_cpus=10,
    hopla_optional=["dir", "verbose", "mylist"])
pprint(exitcodes)

# Local execution with log
status, exitcodes = hopla(
    script, dir=[apath, apath, apath], b=[False, True, False], verbose=1,
    mylist=[1, 2],
    hopla_iterative_kwargs=["dir", "b"], hopla_verbose=1, hopla_cpus=10,
    hopla_outputdir=apath, hopla_logfile=os.path.join(apath, "log"),
    hopla_optional=["dir", "verbose", "mylist"])
pprint(exitcodes)

# Cluster execution
status, exitcodes = hopla(
    script, dir=[apath, apath, apath], b=[False, True, False], verbose=1,
    mylist=[1, 2],
    hopla_iterative_kwargs=["dir", "b"], hopla_verbose=1, hopla_cpus=10,
    hopla_outputdir=apath, hopla_logfile=os.path.join(apath, "log"),
    hopla_optional=["dir", "verbose", "mylist"], hopla_cluster=True,
    hopla_cluster_logdir=cluster_logdir,
    hopla_cluster_queue="Cati_LowPrio",
    hopla_cluster_python_cmd="/usr/bin/python2.7")
pprint(exitcodes)
