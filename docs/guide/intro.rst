.. _intro:

##########
User Guide
##########

Here find some examples of how you might put the S4-Clarity library to use.

***********
EPP Scripts
***********

================
Example StepEPPs
================

Generate CSV
------------

Generate a simple CSV file and attach it to a step.

This EPP extends :class:`s4.clarity.scripts.StepEPP` and is meant to be initiated from a *Record Details* button.

*Record Details Button*

.. code-block:: bash

    bash -c "/opt/gls/clarity/customextensions/env/bin/python
    /opt/gls/clarity/customextensions/examples/generate_csv.py -u {username} -p {password}
    -l {compoundOutputFileLuid0} --step-uri {stepURI} --fileId {compoundOutputFileLuid1}
    --fileName 'example.csv' --artifactUDFName Concentration"

.. literalinclude:: ../examples/generate_csv.py

=========================
Example TriggeredStepEPPs
=========================

QC Set Next Step
----------------

Sets the *next step* action for each output analyte.

This EPP extends :class:`s4.clarity.scripts.TriggeredStepEPP` and is meant to be triggered on the transition into
the *Next Steps* screen, and again on the *End of Step* transition.

*Record Details Exit transition:*

.. code-block:: bash

    bash -c "/opt/gls/clarity/customextensions/env/bin/python
    /opt/gls/clarity/customextensions/examples/qc_set_next_step.py -u {username} -p {password}
    -l {compoundOutputFileLuid0} --step-uri {stepURI} --action RecordDetailsExit"

*End of Step transition:*

.. code-block:: bash

    bash -c "/opt/gls/clarity/customextensions/env/bin/python
    /opt/gls/clarity/customextensions/examples/qc_set_next_step.py -u {username} -p {password}
    -l {compoundOutputFileLuid0} --step-uri {stepURI} --action EndOfStep"

.. literalinclude:: ../examples/qc_set_next_step.py

Create Pools of Two
-------------------

Groups the step's input analytes into pools of two.

This EPP extends :class:`s4.clarity.scripts.TriggeredStepEPP` and is meant to be triggered on the transition into *Pooling*.

*Pooling Enter transition:*

.. code-block:: bash

    bash -c "/opt/gls/clarity/customextensions/env/bin/python
    /opt/gls/clarity/customextensions/examples/create_pools_of_two.py -u {username} -p {password}
    -l {compoundOutputFileLuid0} --step-uri {stepURI} --action PoolingEnter"

.. literalinclude:: ../examples/create_pools_of_two.py

================================
Example DerivedSampleAutomations
================================

Set UDF Value
-------------

Assigns a user provided value to the analyte UDF specified for all selected analytes.

This EPP extends :class:`s4.clarity.scripts.DerivedSampleAutomation` and is meant to be triggered from the projects dashboard.

*Automation Configuration*

.. code-block:: bash

    bash -c "/opt/gls/clarity/customextensions/env/bin/python
    /opt/gls/clarity/customextensions/examples/set_udf_value.py -u {username} -p {password}
    -a '{baseURI}v2' -d {derivedSampleLuids}  --udfName '{userinput:UDF_Name}' --udfValue '{userinput:UDF_Value}'"

.. literalinclude:: ../examples/set_udf_value.py

*************
Shell Scripts
*************

========================
Accession Clarity Sample
========================

Accessions a new sample into Clarity using the provided container name and project.

This script extends :class:`s4.clarity.scripts.ShellScript` and is meant to be executed from the command line.

*Example Invocation*

.. code-block:: bash

    python ./accession_clarity_sample.py -u <user name> -p <password> -r https://<clarity_server>/api/v2
    --sampleName <Sample Name> --projectName <Project Name> --containerName <Container Name>

.. literalinclude:: ../examples/accession_clarity_sample.py

****************
Workflow Testing
****************

============
Workflow Run
============

Runs two samples through a three step protocol.

**Example Invocation**

.. code-block:: bash

     python ./workflow_run.py -u <user name> -p <password> -r https://<clarity_server>/api/v2

.. literalinclude:: ../examples/workflow_run.py
