.. _sphx_glr_auto_gallery:

Examples
========

From within an environment with ``hopla`` installed, you can seamlessly connect
to a cluster, configure nodes, and deploy applications while managing
resources and scaling workloads by running dynamic scripts. The execution
pipeline is as follows:

- **Cluster Configuration**: All cluster settings are stored within the 
  Executor context manager, ensuring a centralized and consistent
  configuration.

- **Job Submission**: The Executor context manager enables you to submit
  delayed jobs, allowing for deferred execution based on resource
  availability and job priorities.

- **Start the Job**: You can manually start and stop these jobs, or leverage
  the Executor context manager to automatically launch them, controlling
  the number of jobs running concurrently to optimize resource utilization.

- **Execution Reporting**: Finally, the Executor context manager provides
  an execution report, offering insights into the status, performance, and
  resource usage of each job executed within the cluster.

``hopla`` is designed to run embarrassingly parallel jobs, i.e. independent
processes in parallel. We recommand to use containers for that purpose.
These jobs need no communications.


How It Works
------------

- **Executor Context**: The `Executor` context manages all cluster
  configurations and task execution.

- **Submit a Job**: The function `executor.submit()` configure a delayed
  job to the Executor. 

- **Start the Job**: You can either start the job manually or have it
  automatically executed when `executor()` is called. You can control
  concurrency by setting `max_jobs` to limit the number of tasks running
  simultaneously. You can also only generate the batch file associated to
  a job `job.generate_batch()`.

- **Execution Reporting**: Once the job completes, the result is retrieved in
  the `executor.reprot` variable.


PBS cluster
-----------

Execution of 10 simple `sleep` commands::

    import hopla
    from pprint import pprint

    executor = hopla.Executor(folder="/tmp/hopla", queue="Nspin_short",
                              walltime=1)

    jobs = [
        executor.submit("sleep", k) for k in range(1, 11)
    ]
    pprint(jobs)

    executor(max_jobs=2)
    print(executor.report)

.. tip::

    To execute a brainprep command available in an apptainer image, adapt and
    pass this command to the `executor.submit()` function::

        apptainer run --bind <path> --cleanenv <image_path> brainprep <args>


CCC cluster
-----------

Execution of 10 simple `sleep` commands available in an docker image::

    import hopla
    from pprint import pprint

    executor = hopla.Executor(folder="/tmp/hopla", queue="rome",
                              walltime=1, project_id="genXXX",
                              image="/tmp/hopla/my-docker-img.tar")

    jobs = [
        executor.submit("-- sleep", k) for k in range(1, 11)
    ]
    pprint(jobs)

    executor(max_jobs=2)
    print(executor.report)

Execution of 10 simple `sleep` commands available in an docker image using a
multi tasks strategy (3 chunks here)::

    chunks = np.array_split(range(1, 11), 3)
    jobs = [
        executor.submit([hopla.DelayedSubmission("-- sleep", k) for k in c])
        for c in chunks
    ]

Since we are using "pcocc-rs" command to run a container, we need to add "--"
to the "sleep" to differentiate pcocc-rs commands and the container commands


.. tip::

    You need to adapt the 
    
the `n_multi_cpus` parameter of the `Executor` in
    order to fit your need. Don't forget to check that your task fulfill the
    folowing core/memory ratios:
    
    - skylake parititon: 3.6G per core.
    - rome partition: 1.7G par core.

.. tip::

    To execution a brainprep command available in an docker image, adapt and
    pass this command to the `executor.submit()` function::

        brainprep <args>

.. important::

    Don't forget to decalre the `n4h00001` hub by copying the 
    `.../n4h00001/n4h00001/config/repositories.yaml` file in your home directory
    `$HOME/.config/pcocc/repositories.yaml`.To list images don't forget to
    also to export the `CCCWORKDIR` env variable to `n4h00001/n4h00001/gaia`.

.. important::

    Don't forget to load the `gcc/11.1.0` module to launch multi tasks jobs,.. tip::

    As  
    and the `python3/3.12` (or another compatible version of Python) module.
    Dont't forget also to switch to the appropriate `dfldatadir/XXX` module.


.. tip::

    You can't export your docker image in a `.tar` file as follows::

        docker save my-docker-img -o my-docker-img.tar 


.. contents:: **Contents**
    :local:
    :depth: 1

