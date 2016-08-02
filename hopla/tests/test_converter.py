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
import sys
# COMPATIBILITY: since python 3.3 mock is included in unittest module
python_version = sys.version_info
if python_version[:2] <= (3, 3):
    import mock
else:
    import unittest.mock as mock

# Hopla import
# Apparently the 'hopla' modules must be imported after coverage is started.
from hopla.converter import hopla
import hopla as root


class TestConverterHopla(unittest.TestCase):
    """ Test the converter module.
    """
    def setUp(self):
        """ Define some parameters.
        """
        self.demodir = os.path.abspath(os.path.dirname(root.__file__))
        self.script = os.path.join(self.demodir, "demo", "my_ls_script.py")

    def test_notlistiter_raises(self):
        """ Not a list for an iterative kwargs -> raise ValueError.
        """
        self.assertRaises(
            ValueError, hopla, self.script, d=["dir1", "dir2"], l=[2, 3],
            fbreak=False, verbose=0, hopla_iterative_kwargs=["d", "verbose"])

    def test_notitersamelength_raises(self):
        """ Not iterative kwargs of same length -> raise ValueError.
        """
        self.assertRaises(
            ValueError, hopla, self.script, d=["dir1", "dir2"], l=[2, 3],
            fbreak=False, verbose=[0, 1, 0],
            hopla_iterative_kwargs=["d", "verbose"])

    @mock.patch("hopla.converter.scheduler")
    def test_normal_execution(self, mock_scheduler):
        """ Test normal execution.
        """
        # Local execution
        for fbreak in (True, False):
            hopla(self.script, d=["dir1"], l=[2, 3], fbreak=fbreak,
                  verbose=[0], hopla_iterative_kwargs=["d", "verbose"],
                  hopla_optional=["fbreak", "verbose"])
            generated_commands = mock_scheduler.call_args_list[-1][0][0]
            expected_commands = [
                [self.script, "-d", "dir1", "--verbose", "0", "-l", "2", "3"]]
            if fbreak:
                expected_commands[0].insert(5, "--fbreak")
            self.assertEqual(sorted(generated_commands),
                             sorted(expected_commands))

        # Local execution with boolean iter
        for fbreak in (True, False):
            hopla(self.script, d=["dir1"], l=[2, 3], fbreak=[fbreak],
                  verbose=0, hopla_iterative_kwargs=["d", "fbreak"],
                  hopla_optional=["fbreak", "verbose"])
            generated_commands = mock_scheduler.call_args_list[-1][0][0]
            expected_commands = [
                [self.script, "-d", "dir1", "-l", "2", "3", "--verbose", "0"]]
            if fbreak:
                expected_commands[0].insert(3, "--fbreak")
            self.assertEqual(generated_commands, expected_commands)


if __name__ == "__main__":
    unittest.main()
