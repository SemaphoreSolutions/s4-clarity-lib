# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from .genericscript import GenericScript
from .stepepp import StepEPP
from .shell import ShellScript
from .triggered_step_epp import TriggeredStepEPP
from .derived_sample_automation import DerivedSampleAutomation
from .user_message_exception import UserMessageException
from .workflow_test import WorkflowTest

module_members = [
    DerivedSampleAutomation,
    GenericScript,
    ShellScript,
    StepEPP,
    TriggeredStepEPP,
    UserMessageException,
    WorkflowTest
]

__all__ = [m.__name__ for m in module_members]

# The below __module__ assignments allow Sphinx to generate links that point to this parent module.
for member in module_members:
    member.__module__ = "s4.clarity.scripts"
