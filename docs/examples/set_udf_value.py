# Copyright 2019 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import argparse

from s4.clarity.scripts import DerivedSampleAutomation


class SetUDFValue(DerivedSampleAutomation):

    @classmethod
    def add_arguments(cls, argparser):
        # type: (argparse) -> None
        super(SetUDFValue, cls).add_arguments(argparser)
        argparser.add_argument("--udfName",
                               type=str,
                               help="The name of the analyte UDF",
                               required=True)
        argparser.add_argument("--udfValue",
                               type=str,
                               help="The new value for the UDF",
                               required=True)

    def process_derived_samples(self):
        for artifact in self.artifacts:
            artifact[self.options.udfName] = self.options.udfValue

        self.lims.artifacts.batch_update(self.artifacts)

        return "Successfully set UDF '%s' to '%s' for %s derived samples" % \
               (self.options.udfName, self.options.udfValue, len(self.artifacts))


if __name__ == "__main__":
    SetUDFValue.main()
