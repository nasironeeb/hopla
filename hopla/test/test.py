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
from pprint import pprint

# Bredala import
from hopla import scheduler
import hopla.demo as demo


class TestHopla(unittest.TestCase):
    """ Test the module functionalities.
    """
    def test_system_commands(self):
        """ Test system commands execution.
        """
        apath = os.path.abspath(os.path.dirname(__file__))
        script = os.path.join(os.path.dirname(demo.__file__),
                              "my_ls_script.py")
        commands = [[script, "-d", apath]] * 10
        status, exitcodes = scheduler(commands, cpus=10, verbose=0)
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
