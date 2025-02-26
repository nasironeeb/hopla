**Usage**

|PythonVersion|_ |License|_ |PoweredBy|_

**Development**

|Pep8|_ |Doc|_

**Release**

|PyPi|_


.. |PythonVersion| image:: https://img.shields.io/badge/python-3.8%20%7C%203.12-blue
.. _PythonVersion: https://github.com/AGrigis/hopla

.. |Pep8| image:: https://github.com/AGrigis/hopla/actions/workflows/pep8.yml/badge.svg
.. _Pep8: https://github.com/AGrigis/hopla/actions

.. |PyPi| image:: https://badge.fury.io/py/hopla.svg
.. _PyPi: https://badge.fury.io/py/hopla

.. |Doc| image:: https://github.com/AGrigis/hopla/actions/workflows/documentation.yml/badge.svg
.. _Doc: http://AGrigis.github.io/hopla

.. |License| image:: https://img.shields.io/badge/License-CeCILLB-blue.svg
.. _License: http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html

.. |PoweredBy| image:: https://img.shields.io/badge/Powered%20by-CEA%2FNeuroSpin-blue.svg
.. _PoweredBy: https://joliot.cea.fr/drf/joliot/Pages/Entites_de_recherche/NeuroSpin.aspx


Hopla!
======


What is hopla?
--------------

Hopla is a lightweight tool for submitting script for computation within a PBS
cluster. It basically wraps submission and provide access to logs.


Important links
---------------

- Official source code repo: https://github.com/AGrigis/hopla
- HTML documentation: http://AGrigis.github.io/hopla


Usage
-----

From inside an environment with hopla installed::

    import hopla
    from pprint import pprint

    executor = hopla.Executor(folder="/tmp/hopla", queue="Nspin_short",
                              walltime=1)

    jobs = [executor.submit("sleep", k) for k in range(1, 11)]
    pprint(jobs)

    executor(max_jobs=2)
    print(executor.report)


Install
-------

Stable release::

    pip install hopla

Main branch::

    pip install https://github.com/AGrigis/hopla.git
