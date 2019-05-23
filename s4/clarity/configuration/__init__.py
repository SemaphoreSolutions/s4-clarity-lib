# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from .protocol import Protocol, StepConfiguration
from .workflow import Workflow
from .process_type import ProcessType, ProcessTemplate, Automation, ProcessInput, ProcessOutput, Parameter, \
    QueueField, IceBucketField, ProcessTypeAttribute, ProcessStepProperty, ProcessEppTrigger, ProcessPermittedInstrumentType
from .udf import Udf, Field
from .stage import Stage

module_members = [
    Automation,
    ProcessTemplate,
    ProcessType,
    Protocol,
    Stage,
    StepConfiguration,
    Udf,
    Field,
    Workflow,
    ProcessInput,
    ProcessOutput,
    Parameter,
    QueueField,
    IceBucketField,
    ProcessTypeAttribute,
    ProcessStepProperty,
    ProcessEppTrigger,
    ProcessPermittedInstrumentType,
]

__all__ = [m.__name__ for m in module_members]

# The below __module__ assignments allow Sphinx to generate links that point to this parent module.
for member in module_members:
    member.__module__ = "s4.clarity.configuration"
