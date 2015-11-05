#! /usr/bin/env python
##########################################################################
# Bredala - Copyright (C) AGrigis, 2015
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
from setuptools import setup, find_packages
from os.path import join, dirname
import hopla
import sys


description = open(join(dirname(__file__), "README.rst")).read()
pkgdata = {
    "hopla.test": ["*.py"],
}

setup(
    name="hopla",
    version=hopla.__version__,
    author="Antoine Grigis",
    author_email="antoine.grigis@cea.fr",
    description=next(x for x in description.splitlines() if x.strip()),
    long_description='.. contents::\n\n' + description,
    url="http://github.com/AGrigis/hopla",
    license='GPL 2+',
    platforms=['any'],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 or "
        "later (GPLv2+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
    ],
    packages=find_packages(),
    package_data=pkgdata,
    install_requires=[]
)
