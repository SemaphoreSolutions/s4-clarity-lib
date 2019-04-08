# Copyright 2019 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import logging

from s4.clarity.artifact import Artifact
from s4.clarity.scripts import TriggeredStepEPP

log = logging.getLogger(__name__)


class QCSetNextStep(TriggeredStepEPP):

    def should_repeat_step(self, input_analyte):
        # type: (Artifact) -> bool

        # QC flag is set on output result file artifacts
        output_measurements = self.step.details.input_keyed_lookup[input_analyte]

        # If QC failed for any replicate of the input it should repeat
        return any(output.qc_failed() for output in output_measurements)

    def on_record_details_exit(self):
        """
        Set the next step actions for the user to inspect.
        """
        for analyte, action in self.step.actions.artifact_actions.items():

            if self.should_repeat_step(analyte):
                log.info("Setting Analyte '%s' (%s) to repeat step." % (analyte.name, analyte.limsid))
                action.repeat()
            else:
                action.next_step()

        self.step.actions.commit()

    def on_end_of_step(self):
        """
         Ensure analytes repeat the step but do not overwrite other user selections.
        """

        # As this is a QC step it is the inputs that are moving to the next step.
        for input_analyte, action in self.step.actions.artifact_actions.items():

            if self.should_repeat_step(input_analyte):
                log.info("Setting Analyte '%s' (%s) to repeat step." % (input_analyte.name, input_analyte.limsid))
                action.repeat()

        self.step.actions.commit()


if __name__ == "__main__":
    QCSetNextStep.main()
