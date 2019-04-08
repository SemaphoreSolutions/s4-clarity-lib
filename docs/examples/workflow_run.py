# Copyright 2019 Semaphore Solutions, Inc.
#
# Assumes a single protocol workflow that consists of three steps:
# - QC
# - Pooling
# - Standard
# ---------------------------------------------------------------------------

import logging

from s4.clarity.configuration import Workflow
from s4.clarity.container import Container
from s4.clarity.project import Project
from s4.clarity.sample import Sample
from s4.clarity.scripts import WorkflowTest
from s4.clarity.steputils.placement_utils import auto_place_artifacts
from s4.clarity.steputils.step_runner import StepRunner

log = logging.getLogger(__name__)

NAME_PROTOCOL = "Testing Protocol"


class QCStepRunner(StepRunner):
    def __init__(self, lims):
        super(QCStepRunner, self).__init__(lims, NAME_PROTOCOL, "QC Step")

    def record_details(self):
        # Set the QC flag on all output measurements
        for output in self.step.details.outputs:
            output.qc = True

        self.lims.artifacts.batch_update(self.step.details.outputs)

    def next_steps(self):
        self.step.actions.all_next_step()
        self.step.actions.commit()


class PoolingStepRunner(StepRunner):
    def __init__(self, lims):
        super(PoolingStepRunner, self).__init__(lims, NAME_PROTOCOL, "Pooling Step")

    def pooling(self):
        # Pool all inputs together
        self.step.pooling.create_pool("The Pool", self.step.details.inputs)
        self.step.pooling.commit()

    def record_details(self):
        # Set a step UDF named "Status"
        self.step.details['Status'] = "Pooling Complete"
        self.step.details.commit()

    def next_steps(self):
        self.step.actions.all_next_step()
        self.step.actions.commit()


class StandardStepRunner(StepRunner):
    def __init__(self, lims):
        super(StandardStepRunner, self).__init__(lims, NAME_PROTOCOL, "Standard Step")

    def placement(self):
        auto_place_artifacts(self.step, self.step.details.outputs)

    def record_details(self):
        # Add all required reagents
        self.add_default_reagents()

        # Set the value of an analyte UDF on all of the outputs.
        for output in self.step.details.outputs:
            output["Inspected By"] = self.step.process.technician.last_name

        self.lims.artifacts.batch_update(self.step.details.outputs)

    def next_steps(self):
        self.step.actions.all_next_step()
        self.step.actions.commit()


class ExampleWorkflowTest(WorkflowTest):
    PROJECT_OWNER_USER_NAME = "admin"
    WORKFLOW_NAME = "Testing Workflow"

    def get_or_create_project(self, project_name):
        # type: (str) -> Project
        projects = self.lims.projects.query(name=project_name)
        if len(projects) > 0:
            log.info("Using existing project %s" % project_name)
            return projects[0]

        project = self.lims.projects.new(name=project_name)
        project.researcher = self.lims.researchers.query(username=self.PROJECT_OWNER_USER_NAME)[0]

        # Submit the project back to Clarity
        self.lims.projects.add(project)
        log.info("Created project %s" % project_name)
        return project

    def get_workflow(self):
        # type: () -> Workflow
        workflow = self.lims.workflows.get_by_name(self.WORKFLOW_NAME)
        if workflow is None:
            raise Exception("Workflow '%s' does not exist in Clarity.")

        return workflow

    def create_tube(self):
        # type: () -> Container
        tube_type = self.lims.container_types.query(name="Tube")[0]
        container = self.lims.containers.new(container_type=tube_type)

        return self.lims.containers.add(container)

    def create_sample(self, name):
        # type: (str) -> Sample
        project = self.get_or_create_project("Today's Project")
        sample = self.lims.samples.new(name=name, project=project)

        # Set the sample container
        container = self.create_tube()
        sample.set_location_coords(container, 1, 1)

        return self.lims.samples.add(sample)

    def run(self, *args):
        log.info("Accessioning samples")
        samples = [
            self.create_sample('Jane'),
            self.create_sample('Bob')
        ]

        log.info("Routing sample to beginning of workflow '%s'", self.WORKFLOW_NAME)
        workflow = self.get_workflow()
        workflow.enqueue([s.artifact for s in samples])

        log.info("Running sample through workflow '%s'", self.WORKFLOW_NAME)
        input_uris = [s.artifact.uri for s in samples]

        qc_step_runner = QCStepRunner(self.lims)
        qc_step_runner.run(inputuris=input_uris)

        pooling_step_runner = PoolingStepRunner(self.lims)
        pooling_step_runner.run(previousstep=qc_step_runner.step)

        StandardStepRunner(self.lims).run(previousstep=pooling_step_runner.step)

        log.info("Sample successfully pushed through workflow '%s'", self.WORKFLOW_NAME)


if __name__ == "__main__":
    ExampleWorkflowTest.main()
