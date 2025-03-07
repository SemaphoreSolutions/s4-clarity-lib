.. _clarity:

================
Clarity Elements
================

Listed here are the definitions for classes that mirror the XML entities used by the Clarity API.

Artifact
--------

.. autoclass:: s4.clarity.artifact.Artifact
    :members:
    :show-inheritance:

Artifact Action
---------------

.. autoclass:: s4.clarity.step.ArtifactAction
    :members:

Artifact Demux
--------------

.. autoclass:: s4.clarity.artifact.ArtifactDemux
    :members:
    :show-inheritance:

Automation
---------------

.. autoclass:: s4.clarity.configuration.Automation
    :members:

Available Input
---------------

.. autoclass:: s4.clarity.step.AvailableInput
    :members:

Clarity Element
---------------

.. autoclass:: s4.clarity.ClarityElement
    :members:

Clarity Exception
-----------------

.. autoclass:: s4.clarity.ClarityException
    :members:
    :show-inheritance:

Container
---------

.. autoclass:: s4.clarity.container.Container
    :members:
    :show-inheritance:

Container Dimension
-------------------

.. autoclass:: s4.clarity.container.ContainerDimension
    :members:
    :show-inheritance:

Container Type
--------------

.. autoclass:: s4.clarity.container.ContainerType
    :members:

Control Type
------------

.. autoclass:: s4.clarity.control_type.ControlType
    :members:
    :show-inheritance:

Demux Artifact
--------------

.. autoclass:: s4.clarity.artifact.DemuxArtifact
    :members:
    :show-inheritance:

Demux Details
-------------

.. autoclass:: s4.clarity.artifact.DemuxDetails
    :members:
    :show-inheritance:

Element Factory
---------------

.. autoclass:: s4.clarity.ElementFactory
    :members:

Fields Mixin
------------

.. autoclass:: s4.clarity._internal.FieldsMixin
    :members:

File
----

.. autoclass:: s4.clarity.file.File
    :members:
    :show-inheritance:

Instrument
----------

.. autoclass:: s4.clarity.instrument.Instrument
    :members:
    :show-inheritance:

Instrument Type
---------------

.. autoclass:: s4.clarity.configuration.InstrumentType
    :members:
    :show-inheritance:

IO Map
------

.. autoclass:: s4.clarity.iomaps.IOMap
    :members:

Lab
---

.. autoclass:: s4.clarity.lab.Lab
    :members:
    :show-inheritance:

LIMS
----

.. autoclass:: s4.clarity.LIMS
    :members:

Output Reagent
--------------

.. autoclass:: s4.clarity.step.OutputReagent
    :members:

Permission
----------

.. autoclass:: s4.clarity.permission.Permission
    :members:
    :show-inheritance:

Placement
------------

.. autoclass:: s4.clarity.step.Placement
    :members:

Pool
------------

.. autoclass:: s4.clarity.step.Pool
    :members:

Process
-------

.. autoclass:: s4.clarity.process.Process
    :members:
    :show-inheritance:

    .. automethod:: commit
    .. automethod:: get
    .. automethod:: get_formatted_number_string
    .. automethod:: get_raw
    .. automethod:: get_udf_config
    .. automethod:: invalidate
    .. automethod:: iomaps_input_keyed
    .. automethod:: iomaps_output_keyed
    .. automethod:: refresh

    .. autoattribute:: fields
    .. autoattribute:: limsid

Process Template
----------------

.. autoclass:: s4.clarity.configuration.ProcessTemplate
    :members:
    :show-inheritance:

Process Type
------------

.. autoclass:: s4.clarity.configuration.ProcessType
    :members:
    :show-inheritance:

Project
-------

.. autoclass:: s4.clarity.project.Project
    :members:
    :show-inheritance:

Protocol
--------

.. autoclass:: s4.clarity.configuration.Protocol
    :members:
    :show-inheritance:

Protocol Step Field
-------------------

.. autoclass:: s4.clarity.configuration.ProtocolStepField
    :members:

Queue
-----

.. autoclass:: s4.clarity.queue.Queue
    :members:
    :show-inheritance:

Reagent Kit
-----------

.. autoclass:: s4.clarity.reagent_kit.ReagentKit
    :members:
    :show-inheritance:

Reagent Lot
-----------

.. autoclass:: s4.clarity.reagent_lot.ReagentLot
    :members:
    :show-inheritance:

Reagent Type
------------

.. autoclass:: s4.clarity.reagent_type.ReagentType
    :members:
    :show-inheritance:

Researcher
----------

.. autoclass:: s4.clarity.researcher.Researcher
    :members:
    :show-inheritance:

Role
----

.. autoclass:: s4.clarity.role.Role
    :members:
    :show-inheritance:

Router
------

.. autoclass:: s4.clarity.routing.Router
    :members:

Sample
------

.. autoclass:: s4.clarity.sample.Sample
    :members:
    :show-inheritance:

Stage
-----

.. autoclass:: s4.clarity.configuration.Stage
    :members:
    :show-inheritance:

Step
----

.. autoclass:: s4.clarity.step.Step
    :members:
    :show-inheritance:

Step Actions
------------

.. autoclass:: s4.clarity.step.StepActions
    :members:
    :show-inheritance:

Step Configuration
------------------

.. autoclass:: s4.clarity.configuration.StepConfiguration
    :members:
    :show-inheritance:

Step Details
------------

.. autoclass:: s4.clarity.step.StepDetails
    :members:
    :show-inheritance:

    .. automethod:: commit
    .. automethod:: get
    .. automethod:: get_formatted_number_string
    .. automethod:: get_raw
    .. automethod:: get_udf_config
    .. automethod:: invalidate
    .. automethod:: iomaps_input_keyed
    .. automethod:: iomaps_output_keyed
    .. automethod:: refresh

    .. autoattribute:: fields
    .. autoattribute:: limsid

Step Factory
------------

.. autoclass:: s4.clarity.StepFactory
    :members:
    :show-inheritance:

Step Placements
---------------

.. autoclass:: s4.clarity.step.StepPlacements
    :members:
    :show-inheritance:

Step Pools
------------

.. autoclass:: s4.clarity.step.StepPools
    :members:
    :show-inheritance:

Step Program Status
-------------------

.. autoclass:: s4.clarity.step.StepProgramStatus
    :members:
    :show-inheritance:

Step Reagents
-------------

.. autoclass:: s4.clarity.step.StepReagents
    :members:
    :show-inheritance:

Step Reagent Lots
-----------------

.. autoclass:: s4.clarity.step.StepReagentLots
    :members:
    :show-inheritance:

Step Trigger
------------

.. autoclass:: s4.clarity.step.StepTrigger
    :members:

UDF
---

.. autoclass:: s4.clarity.configuration.Udf
    :members:
    :show-inheritance:

UDF Factory
-----------

.. autoclass:: s4.clarity.UdfFactory
    :members:
    :show-inheritance:

Workflow
--------

.. autoclass:: s4.clarity.configuration.Workflow
    :members:
    :show-inheritance:

Workflow Stage History
----------------------

.. autoclass:: s4.clarity.artifact.WorkflowStageHistory
    :members:
