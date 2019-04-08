# Copyright 2019 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import logging
import argparse
from csv import DictWriter

from s4.clarity.scripts import StepEPP

HEADER_INPUT_NAME = "Input Name"
HEADER_INPUT_ID = "Input Id"
HEADER_OUTPUT_NAME = "Output Name"
HEADER_OUTPUT_ID = "Output Id"

log = logging.getLogger(__name__)


class GenerateCSV(StepEPP):

    @classmethod
    def add_arguments(cls, argparser):
        # type: (argparse) -> None
        super(GenerateCSV, cls).add_arguments(argparser)
        argparser.add_argument("--fileId",
                               help="{compoundOutputFileLuids} token",
                               required=True)
        argparser.add_argument("--fileName",
                               type=str,
                               help="File name with extension",
                               default="epp_generated.csv")
        argparser.add_argument("--artifactUDFName",
                               type=str,
                               help="Name of the UDF to include in file",
                               required=True)

    def run(self):
        csv_file = self.step.open_resultfile(self.options.fileName, 'w', limsid=self.options.fileId)

        csv_writer = DictWriter(csv_file, fieldnames=[
            HEADER_INPUT_NAME,
            HEADER_INPUT_ID,
            HEADER_OUTPUT_NAME,
            HEADER_OUTPUT_ID,
            self.options.artifactUDFName
        ])

        csv_writer.writeheader()

        for input_analyte, output_analytes in self.step.details.input_keyed_lookup.items():
            for output_analyte in output_analytes:
                udf_value = output_analyte.get(self.options.artifactUDFName, "Empty")

                row = {
                    HEADER_INPUT_NAME: input_analyte.name,
                    HEADER_INPUT_ID: input_analyte.limsid,
                    HEADER_OUTPUT_NAME: output_analyte.name,
                    HEADER_OUTPUT_ID: output_analyte.limsid,
                    self.options.artifactUDFName: udf_value
                }

                log.info("Writing the following line: %s" % row)

                csv_writer.writerow(row)

        csv_file.commit()


if __name__ == "__main__":
    GenerateCSV.main()
