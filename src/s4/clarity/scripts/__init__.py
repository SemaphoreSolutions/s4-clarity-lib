# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from s4.clarity.scripts.genericscript import GenericScript
from s4.clarity.scripts.stepepp import StepEPP
from s4.clarity.scripts.shell import ShellScript
from s4.clarity.scripts.triggered_step_epp import TriggeredStepEPP
from s4.clarity.scripts.derived_sample_automation import DerivedSampleAutomation
from s4.clarity.scripts.user_message_exception import UserMessageException
from s4.clarity.scripts.workflow_test import WorkflowTest

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
