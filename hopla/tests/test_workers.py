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
import tempfile
import shutil
import multiprocessing
import time

# Hopla import
# Apparently the 'hopla' modules must be imported after coverage is started
import hopla as root
from hopla.converter import hopla
from hopla.workers import worker
from hopla.workers import qsub_worker
from hopla.signals import FLAG_ALL_DONE
from hopla.signals import FLAG_WORKER_FINISHED_PROCESSING


class TestSchedulerHopla(unittest.TestCase):
    """ Test the scheduler module.
    """
    def setUp(self):
        """ Define some parameters.
        """
        self.demodir = os.path.abspath(os.path.dirname(root.__file__))
        self.script = os.path.join(self.demodir, "demo", "my_ls_script.py")

    def create_jobs(self):
        """ Create a new test settings.
        """
        tasks = multiprocessing.Queue()
        returncodes = multiprocessing.Queue()
        commands = [[self.script, "-d", self.demodir, "-l", "1", "2"]] * 5
        for cnt, cmd in enumerate(commands):
            job_name = "job_{0}".format(cnt)
            tasks.put((job_name, cmd))
        tasks.put(FLAG_ALL_DONE)

        return tasks, returncodes

    def test_worker_execution(self):
        """ Test local worker.
        """
        tasks, returncodes = self.create_jobs()
        worker(tasks, returncodes)
        time.sleep(1)
        outputs = []
        while not returncodes.empty():
            outputs.append(returncodes.get())
        self.assertEqual(len(outputs), 5 + 1)
        self.assertEqual(outputs[-1], FLAG_WORKER_FINISHED_PROCESSING)

    def test_qsubworker_execution(self):
        """ Test cluster qsub worker.
        """
        logdir = tempfile.mkdtemp()
        tasks, returncodes = self.create_jobs()
        qsub_worker(tasks, returncodes, logdir, "DUMMY")
        time.sleep(1)
        outputs = []
        while not returncodes.empty():
            outputs.append(returncodes.get())
        self.assertEqual(len(outputs), 5 + 1)
        self.assertEqual(outputs[-1], FLAG_WORKER_FINISHED_PROCESSING)
        shutil.rmtree(logdir)

    def test_local_execution(self):
        """ Test local execution.
        """
        logfile = tempfile.NamedTemporaryFile(suffix=".log").name
        hopla(self.script, d=[self.demodir, self.demodir], l=[2, 3],
              fbreak=[False, True], verbose=0,
              hopla_iterative_kwargs=["d", "fbreak"], hopla_logfile=logfile,
              hopla_cpus=4, hopla_optional=["fbreak", "verbose"])
        os.remove(logfile)

    def test_cluster_execution(self):
        """ Test cluster execution.
        """
        logfile = tempfile.NamedTemporaryFile(suffix=".log").name
        logdir = tempfile.mkdtemp()
        hopla(self.script, d=[self.demodir, self.demodir], l=[2, 3],
              fbreak=[False, True], verbose=0,
              hopla_iterative_kwargs=["d", "fbreak"], hopla_logfile=logfile,
              hopla_cpus=4, hopla_optional=["fbreak", "verbose"],
              hopla_cluster=True, hopla_cluster_logdir=logdir,
              hopla_cluster_queue="DUMMY")
        shutil.rmtree(logdir)
        os.remove(logfile)


if __name__ == "__main__":
    unittest.main()
