# Copyright 2019 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import logging
import argparse

from s4.clarity.scripts import ShellScript

log = logging.getLogger(__name__)


class AccessionClaritySample(ShellScript):

    @classmethod
    def add_arguments(cls, argparser):
        # type: (argparse) -> None
        super(AccessionClaritySample, cls).add_arguments(argparser)
        argparser.add_argument("--sampleName",
                               type=str,
                               help="The name of the sample to create",
                               required=True)
        argparser.add_argument("--projectName",
                               type=str,
                               help="The name of an existing Clarity project",
                               required=True)
        argparser.add_argument("--containerName",
                               type=str,
                               help="The name of the sample container",
                               required=True)

    def run(self, *args):
        projects = self.lims.projects.query(name=self.options.projectName)
        if not projects:
            raise Exception("Project '%s' does not exist in Clarity" % self.options.projectName)

        project = projects[0]

        tube_type = self.lims.container_types.get_by_name("Tube")
        container = self.lims.containers.new(container_type=tube_type, name=self.options.containerName)
        container = self.lims.containers.add(container)

        sample = self.lims.samples.new(name=self.options.sampleName, project=project)
        sample.set_location_coords(container, 1, 1)
        self.lims.samples.add(sample)

        log.info("Sample '%s' successfully accessioned in Clarity" % self.options.sampleName)


if __name__ == "__main__":
    AccessionClaritySample.main()
