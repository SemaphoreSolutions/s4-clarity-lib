# Copyright 2019 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from s4.clarity.scripts import TriggeredStepEPP
from s4.clarity.scripts import UserMessageException


class CreatePoolsOfTwo(TriggeredStepEPP):

    def validate_even_number_of_inputs(self):
        num_input_analytes = len(self.step.pooling.available_inputs)

        if num_input_analytes % 2:
            raise UserMessageException("Step must be started with an even number of analytes.")

    def validate_single_input_replicate_created(self):
        for available_input in self.step.pooling.available_inputs:
            if available_input.replicates > 1:
                raise UserMessageException("No more than one replicate per analyte allowed in this step")

    def on_pooling_enter(self):
        self.validate_single_input_replicate_created()
        self.validate_even_number_of_inputs()

        inputs = [a.input for a in self.step.pooling.available_inputs]

        for i in range(0, len(inputs) - 1, 2):
            pool_inputs = [
                inputs[i],
                inputs[i + 1]
            ]

            pool_name = "%s_%s" % (pool_inputs[0].limsid, pool_inputs[1].limsid)

            self.step.pooling.create_pool(pool_name, pool_inputs)

        self.step.pooling.commit()


if __name__ == "__main__":
    CreatePoolsOfTwo.main()
