hopla usage examples
====================


From inside an environment with hopla installed::

    import hopla
    from pprint import pprint

    executor = hopla.Executor(folder="/tmp/hopla", queue="Nspin_short",
                              walltime=1)

    jobs = [executor.submit("sleep", k) for k in range(1, 11)]
    pprint(jobs)

    executor(max_jobs=2)
    print(executor.report)


.. contents:: **Contents**
    :local:
    :depth: 1

