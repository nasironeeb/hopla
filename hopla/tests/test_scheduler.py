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

# Hopla import
# Apparently the 'hopla' modules must be imported after coverage is started
import hopla as root
from hopla.scheduler import scheduler


class TestSchedulerHopla(unittest.TestCase):
    """ Test the scheduler module.
    """
    def setUp(self):
        """ Define some parameters.
        """
        self.demodir = os.path.abspath(os.path.dirname(root.__file__))
        self.script = os.path.join(self.demodir, "demo", "my_ls_script.py")

    def test_nocmd_raises(self):
        """ No commands to execute -> raise ValueError.
        """
        self.assertRaises(ValueError, scheduler, commands=[])

    def test_noclusterlogdir_raises(self):
        """ No cluster log dir -> raise ValueError.
        """
        self.assertRaises(ValueError, scheduler, commands=[], cluster=True)

    def test_notemptylogdir_raises(self):
        """ Not empty cluster log dir -> raise ValueError.
        """
        self.assertRaises(ValueError, scheduler, commands=[], cluster=True,
                          cluster_logdir=self.demodir)

    def test_noqueue_raises(self):
        """ No cluster queue -> raise ValueError.
        """
        logdir = tempfile.mkdtemp()
        self.assertRaises(ValueError, scheduler, commands=[], cluster=True,
                          cluster_logdir=logdir)
        shutil.rmtree(logdir)

    def test_loghandlers(self):
        """ Test log.
        """
        logging.root.addHandler(logging.NullHandler())
        self.assertRaises(ValueError, scheduler, commands=[],
                          verbose=0)
        self.assertEqual(len(logging.root.handlers), 0)
        self.assertEqual(len(logging.getLogger("hopla").handlers), 1)
        self.assertTrue(isinstance(logging.getLogger("hopla").handlers[0],
                                   logging.NullHandler))
        self.assertRaises(ValueError, scheduler, commands=[],
                          verbose=1)
        self.assertEqual(len(logging.root.handlers), 0)
        self.assertEqual(len(logging.getLogger("hopla").handlers), 1)
        self.assertTrue(isinstance(logging.getLogger("hopla").handlers[0],
                                   logging.StreamHandler))
        logfile = tempfile.NamedTemporaryFile(suffix=".log").name
        self.assertRaises(ValueError, scheduler, commands=[], logfile=logfile,
                          verbose=1)
        self.assertEqual(len(logging.root.handlers), 0)
        self.assertEqual(len(logging.getLogger("hopla").handlers), 2)
        self.assertTrue(isinstance(logging.getLogger("hopla").handlers[0],
                                   logging.StreamHandler))
        self.assertTrue(isinstance(logging.getLogger("hopla").handlers[1],
                                   logging.FileHandler))
        os.remove(logfile)

    def test_normal_execution(self):
        """ Test normal execution.
        """
        logfile = tempfile.NamedTemporaryFile(suffix=".log").name
        outputdir = tempfile.mkdtemp()
        commands = [[self.script, "-d", self.demodir, "-l", "1", "2"]] * 5
        status, exitcodes = scheduler(
            commands, cpus=20, logfile=logfile, outputdir=outputdir)
        for job_name, exitcode in exitcodes.items():
            exitcode += exitcode
            if exitcode > 0:
                pprint(status[job_name]["info"])
        self.assertEqual(exitcode, 0)
        shutil.rmtree(outputdir)
        os.remove(logfile)


if __name__ == "__main__":
    unittest.main()
