#! /usr/bin/env python
##########################################################################
# Hopla - Copyright (C) AGrigis, 2015
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# Bredala import
import bredala
bredala.USE_PROFILER = False
bredala.register("os.path", names=["listdir"])

# System import
import argparse
import os

# Parameters to keep trace
__hopla__ = ["directory", "files"]


def is_directory(dirarg):
    """ Type for argparse - checks that directory exists.
    """
    if not os.path.isdir(dirarg):
        raise argparse.ArgumentError(
            "The directory '{0}' does not exist!".format(dirarg))
    return dirarg


parser = argparse.ArgumentParser(description="List a directory.")
parser.add_argument(
    "-d", "--dir", dest="dir", required=True, metavar="PATH",
    help="a valid directory to be listed.", type=is_directory)
args = parser.parse_args()

directory = args.dir
files = os.listdir(directory)
