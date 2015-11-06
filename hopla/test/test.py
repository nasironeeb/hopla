#! /usr/bin/env python
##########################################################################
# Hopla - Copyright (C) AGrigis, 2015
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import unittest
import os
import logging
from pprint import pprint
import tempfile
import shutil

# Create a 'root' logger
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())

# Hopla import
# Apparently the 'hopla' modules must be imported after coverage is started.
from hopla.scheduler import scheduler
from hopla.converter import hopla
import hopla.demo as demo


class TestHopla(unittest.TestCase):
    """ Test the module functionalities.
    """
    def test_raises(self):
        """ Test dead ends.
        """
        print()
        script = os.path.join(os.path.dirname(demo.__file__),
                              "my_ls_script.py")
        self.assertRaises(Exception, scheduler, [])
        self.assertRaises(
            ValueError, hopla, script, hopla_iterative_kwargs=["d", "verbose"],
            d=["", "", ""], verbose=0)
        self.assertRaises(
            ValueError, hopla, script, hopla_iterative_kwargs=["d", "verbose"],
            d=["", "", ""], verbose=[0, 0])

    def test_scheduler(self):
        """ Test scheduler execution.
        """
        print()
        logfile = tempfile.NamedTemporaryFile(suffix='.log').name
        outputdir = tempfile.mkdtemp()
        for verbosity in [0, 1, 2]:
            apath = os.path.abspath(os.path.dirname(__file__))
            script = os.path.join(os.path.dirname(demo.__file__),
                                  "my_ls_script.py")
            commands = [[script, "-d", apath]] * 5
            status, exitcodes = scheduler(
                commands, cpus=1000, verbose=verbosity, logfile=logfile,
                outputdir=outputdir)
            exitcode = 0
            for job_name, exitcode in exitcodes.items():
                exitcode += exitcode
                if exitcode > 0:
                    pprint(status[job_name]["info"])
            self.assertEqual(exitcode, 0)
        shutil.rmtree(outputdir)
        os.remove(logfile)

    def test_command_warping(self):
        """ Test command warping.
        """
        print()
        apath = os.path.abspath(os.path.dirname(__file__))
        script = os.path.join(os.path.dirname(demo.__file__),
                              "my_ls_script.py")
        for option in [{"verbose": 0}, {"v": 0}]:
            status, exitcodes = hopla(
                script, hopla_iterative_kwargs=["d"], d=[apath, apath, apath],
                hopla_verbose=1, hopla_cpus=2, **option)
            exitcode = 0
            for job_name, exitcode in exitcodes.items():
                exitcode += exitcode
                if exitcode > 0:
                    pprint(status[job_name]["info"])
            self.assertEqual(exitcode, 0)


def test():
    """ Function to execute unitest
    """
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHopla)
    runtime = unittest.TextTestRunner(verbosity=2).run(suite)
    return runtime.wasSuccessful()


if __name__ == "__main__":
    test()
