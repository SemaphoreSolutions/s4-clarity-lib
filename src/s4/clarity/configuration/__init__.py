# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from s4.clarity.configuration.protocol import Protocol, StepConfiguration, ProtocolStepField
from s4.clarity.configuration.workflow import Workflow
from s4.clarity.configuration.process_type import ProcessType, ProcessTemplate, Automation
from s4.clarity.configuration.udf import Udf
from s4.clarity.configuration.stage import Stage

module_members = [
    Automation,
    ProcessTemplate,
    ProcessType,
    Protocol,
    ProtocolStepField,
    Stage,
    StepConfiguration,
    Udf,
    Workflow,
]

__all__ = [m.__name__ for m in module_members]

# The below __module__ assignments allow Sphinx to generate links that point to this parent module.
for member in module_members:
    member.__module__ = "s4.clarity.configuration"
