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
    """ Type for argparse - checks that directory exists.
    """
    if not os.path.isdir(dirarg):
        raise argparse.ArgumentError(
            "The directory '{0}' does not exist!".format(dirarg))
    return dirarg


parser = argparse.ArgumentParser(description="List a directory.")
required = parser.add_argument_group("required arguments")
required.add_argument(
    "-d", "--dir", dest="dir", required=True, metavar="PATH",
    help="a valid directory to be listed.", type=is_directory)
required.add_argument(
    "-o", "--optional", dest="optional", metavar="STR",
    help="an optional string")
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
