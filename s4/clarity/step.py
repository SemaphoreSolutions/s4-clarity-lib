# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import logging
import time
import re

from s4.clarity.artifact import Artifact
from s4.clarity.researcher import Researcher
from s4.clarity import lazy_property

from . import ETree, ClarityException
from . import types
from .instrument import Instrument
from .reagent_lot import ReagentLot
from .container import Container
from .iomaps import IOMapsMixin
from ._internal import ClarityElement, WrappedXml, FieldsMixin
from ._internal.props import subnode_property_list_of_dicts, subnode_property, attribute_property, subnode_link, subnode_links, subnode_element_list

log = logging.getLogger(__name__)

# Step actions that can be assigned in the Next Step drop down
COMPLETE_ACTION = "complete"
REMOVE_FROM_WORKFLOW_ACTION = "remove"
COMPLETE_AND_REPEAT_ACTION = "completerepeat"
REPEAT_STEP_ACTION = "repeat"
REWORK_ACTION = "rework"
REVIEW_ACTION = "review"
STORE_ACTION = "store"
NEXT_STEP_ACTION = "nextstep"

PROGRAM_STATUS_ERROR = "ERROR"
PROGRAM_STATUS_RUNNING = "RUNNING"
PROGRAM_STATUS_QUEUED = "QUEUED"


class Step(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/step}step"

    date_started = subnode_property("date-started", types.DATETIME)
    date_completed = subnode_property("date-completed", types.DATETIME)

    name = subnode_property("configuration", readonly=True)

    def open_resultfile(self, name, mode, only_write_locally=False, limsid=None):
        """
        :type name: str
        :type mode: str
        :type only_write_locally: bool
        :type limsid: str
        :rtype: s4.clarity.File
        """

        if limsid is not None:
            def filterfunc(o):
                return o.limsid == limsid
            filterdesc = "limsid = %s" % limsid
        else:
            def filterfunc(o):
                return o.name == name
            filterdesc = "name = %s" % name

        matches = list(filter(filterfunc, self.details.shared_outputs))

        if not matches:
            raise ValueError("No output file matching filter: " + filterdesc)

        if len(matches) > 1:
            raise ValueError("Multiple output artifacts matching filter: " + filterdesc)

        return matches[0].open_file(mode, only_write_locally, name)

    @lazy_property
    def details(self):
        """
        :type: StepDetails
        """
        return StepDetails(self, self.lims, self.uri + "/details")

    @lazy_property
    def actions(self):
        """
        :type: StepActions
        """
        return StepActions(self.lims, self.uri + "/actions")

    @lazy_property
    def configuration(self):
        """
        :type: StepConfiguration
        """
        node = self.xml_find("./configuration")
        return self.lims.stepconfiguration_from_uri(node.get("uri"))

    @property
    def automatic_next_step(self):
        """
        :type: Step
        """
        return self.lims.steps.from_link_node(self.xml_find("automatic-next-step"))

    @lazy_property
    def pooling(self):
        """
        :type: StepPools
        """
        pool_link_node = self.xml_find("./pools")
        if pool_link_node is None:
            return None
        return StepPools(self, self.lims, pool_link_node.get("uri"))

    @lazy_property
    def placements(self):
        """
        :type: StepPlacements
        """
        placements_node = self.xml_find("./placements")
        if placements_node is None:
            return None
        return StepPlacements(self.lims, placements_node.get("uri"))

    @lazy_property
    def reagent_lots(self):
        """
        :type: StepReagentLots
        """
        return StepReagentLots(self, self.lims, self.uri + "/reagentlots")

    @lazy_property
    def reagents(self):
        """
        :type: StepReagents
        """
        return StepReagents(self, self.lims, self.uri + "/reagents")

    @lazy_property
    def program_status(self):
        """
        :type: StepProgramStatus
        """
        return StepProgramStatus(self.lims, self.uri + "/programstatus")

    @lazy_property
    def available_programs(self):
        """
        :type: StepTrigger
        """
        nodes = self.xml_findall("./available-programs/available-program")
        if nodes is None:
            return None

        return [StepTrigger(self, node) for node in nodes]

    @property
    def process(self):
        """
        :type: Process
        """
        return self.lims.processes.from_limsid(self.limsid)

    @property
    def fields(self):
        """
        :raises NotImplementedError: Steps don't have fields. Use step.details.
        """
        raise NotImplementedError("Steps don't have fields. Use step.details.")

    @property
    def current_state(self):
        """
        :type: str
        """
        return self.xml_root.get("current-state")

    def wait_for_epp(self):
        # type: () -> int
        """
        Polls Clarity, blocking until the currently running EPP is done.

        :raises EppException: When EPP execution fails.
        :return: Zero
        :rtype: int
        """
        try:
            count = 0
            while True:
                self.program_status.refresh()

                if count == 1:
                    log.info("Waiting for EPP.")

                if self.program_status.status not in [PROGRAM_STATUS_RUNNING, PROGRAM_STATUS_QUEUED]:
                    log.info("EPP finished with status %s.", self.program_status.status)

                    if self.program_status.status == PROGRAM_STATUS_ERROR:
                        log.error(self.program_status.message)
                        raise EppFailureException(self.program_status.message)

                    self.refresh()
                    return 0

                time.sleep(1)
                count += 1

        except ClarityException:
            log.info("No EPP found.")
            return 0

    def advance(self):
        # type: () -> None
        """
        Advances the current step to the next screen.
        """

        log.info("Advancing Step.")
        self.xml_root = self.lims.request("post", self.uri + "/advance", self.xml_root)
        self.wait_for_epp()


class EppException(Exception):
    """
    Base class for all exceptions resulting from errors while running an EPP.
    """
    pass


class EppFailureException(EppException):
    """
    Raised when an EPP fails to execute correctly.
    """
    pass


class EPPTimeoutException(EppException):
    """
    Raised when the StepRunner times out waiting on an EPP to complete.
    """
    def __init__(self):
        super(EPPTimeoutException, self).__init__("Step Runner EPP Timeout - Step took too long to get to next state.")


class ArtifactAction(WrappedXml):
    UNIVERSAL_TAG = "{http://genologics.com/ri/step}actions"

    artifact_uri = attribute_property("artifact-uri")
    action = attribute_property("action")
    step_uri = attribute_property("step-uri")
    rework_step_uri = attribute_property("rework-step-uri")

    def __init__(self, lims, step, xml_root):
        super(ArtifactAction, self).__init__(lims, xml_root)
        self.step = step

    def remove_from_workflow(self):
        """
        Sets the Next Step property for the artifact specified by artifact_uri to 'Remove From Workflow'
        """
        self._set_artifact_next_action(REMOVE_FROM_WORKFLOW_ACTION)

    def review(self):
        """
        Sets the Next Step property for the artifact specified by artifact_uri to 'Request Manager Review'
        """
        self._set_artifact_next_action(REVIEW_ACTION)

    def repeat(self):
        """
        Sets the Next Step property for the artifact specified by artifact_uri to 'Repeat Step'
        """
        self._set_artifact_next_action(REPEAT_STEP_ACTION)

    def mark_protocol_complete(self):
        self._set_artifact_next_action(COMPLETE_ACTION)

    def next_step(self, step_uri=None):
        """
        Set the next step to continue to, or mark the protocol as complete if there is no next step.

        If step_uri is not provided, artifact will:
        - Continue to the first transition defined for this step, if any transitions are defined.
        - Mark the protocol as complete, if there are no transitions (the protocol is done).
        """
        transitions = self.step.configuration.transitions

        if len(transitions) == 0:
            self._set_artifact_next_action(COMPLETE_ACTION)
        else:
            step_uri = step_uri or transitions[0]["next-step-uri"]
            self._set_step_uri_action(NEXT_STEP_ACTION, step_uri)

    def complete_and_repeat(self, step_uri):
        """
        Sets the Next Step property for the artifact specified by artifact_uri to 'Complete and Repeat' with the specified next step uri.
        """
        self._set_step_uri_action(COMPLETE_AND_REPEAT_ACTION, step_uri)

    def rework(self, step_uri):
        """
        Sets the Next Step property for the artifact specified by artifact_uri to 'Rework from an earlier step' with the specified next step uri.
        """
        self._set_artifact_next_action(REWORK_ACTION)
        self.rework_step_uri = step_uri

    def _set_artifact_next_action(self, action):
        self.action = action

        # Make sure there are no old routing uris in the element
        self.step_uri = None
        self.rework_step_uri = None

    def _set_step_uri_action(self, action, step_uri):
        self._set_artifact_next_action(action)
        self.step_uri = step_uri


class StepActions(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/step}actions"

    next_actions = subnode_property_list_of_dicts('next-actions/next-action', as_attributes=[
        'artifact-uri', 'action', 'step-uri', 'rework-step-uri'
    ])

    step = subnode_link(Step, "step")

    # The Researcher that was running the step and requested a manager review
    escalation_author = subnode_link(Researcher, "./escalation/request/author", attributes=('uri',), readonly=True)

    # The Researcher that has been flagged as the reviewer for this step
    escalation_reviewer = subnode_link(Researcher, "./escalation/request/reviewer", attributes=('uri',), readonly=True)

    # The date that the step was moved into the 'Under Review' state
    escalation_date = subnode_property("./escalation/request/date", typename=types.DATETIME, readonly=True)

    # All artifacts that are under manager review
    escalated_artifacts = subnode_links(Artifact, "./escalation/escalated-artifacts/escalated-artifact")

    @lazy_property
    def artifact_actions(self):
        """
        A dictionary of ArtifactActions for this step, keyed by artifact.

        :rtype: dict[Artifact, ArtifactAction]
        """
        actions = {}
        for xml_entry in self.xml_findall("./next-actions/next-action"):
            artifact = self.lims.artifacts.get(xml_entry.get("artifact-uri"))
            actions[artifact] = ArtifactAction(self.lims, self.step, xml_entry)
        return actions

    def __str__(self):
        return "<Actions for Step %s>" % self.step.limsid

    def all_next_step(self, step_uri=None):
        """
        Set all artifacts actions to either next step, or mark protocol as complete.

        If step_uri is not provided, artifacts will:
            - Continue to the first transition defined for this step, if any transitions are defined.
            - Mark the protocol as complete, if there are no transitions.
        """

        for action in self.artifact_actions.values():
            action.next_step(step_uri)


class StepDetails(IOMapsMixin, FieldsMixin, ClarityElement):
    """
    :ivar Step step:

    :ivar list[IOMap] iomaps:
    :ivar list[Artifact] inputs:
    :ivar list[Artifact] outputs:
    :ivar list[Artifact] shared_outputs:

    :ivar str|None uri:
    :ivar LIMS lims:
    """

    UNIVERSAL_TAG = "{http://genologics.com/ri/step}details"
    FIELDS_XPATH = "./fields"
    ATTACH_TO_CATEGORY = "ProcessType"
    IOMAPS_XPATH = "input-output-maps/input-output-map"
    IOMAPS_OUTPUT_TYPE_ATTRIBUTE = "type"

    name = subnode_property("configuration", readonly=True)
    instrument_used = subnode_link(Instrument, "instrument", readonly=True, attributes=('uri',))

    def __init__(self, step, *args, **kwargs):
        self.step = step
        super(StepDetails, self).__init__(*args, **kwargs)

    def __str__(self):
        if self.step:
            return "<Details for Step %s>" % self.step.limsid
        else:
            return "<Unattached StepDetails>"

    def sorted_input_sample_iomaps(self):
        "return list of sample iomaps sorted by sample name"
        # extract and convert the number portion of the sample name
        sample_iomaps = [iom for iom in self.iomaps if not iom.input.is_control]

        def process_sample_name(iomap):
            cells = [c for c in re.split(r'(\d+)?(\D+)', iomap.input.name) if c]
            for i, cell in enumerate(cells):
                if cell.isdigit():
                    # format cell length to be zero padded to 2 digits
                    cells[i] = '%02d%s' % (len(cell), cell)
            return ''.join(cells)

        sorted_sample_iomaps = sorted(sample_iomaps, key=process_sample_name)
        return sorted_sample_iomaps

    def _get_attach_to_key(self):
        return self.name, self.ATTACH_TO_CATEGORY

    def _get_iomaps_shared_result_file_type(self):
        return "ResultFile"


class StepPools(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/step}pools"

    def __init__(self, step, lims, uri):
        self.step = step
        super(StepPools, self).__init__(lims, uri)

    def __str__(self):
        return "<Pools for Step %s>" % self.step.limsid

    @property
    def available_inputs(self):
        """
        :type: list[AvailableInput]
        """
        elements = self.xml_findall("./available-inputs/input")
        return [AvailableInput(self.lims, p) for p in elements]

    @property
    def pools(self):
        """
        :type: list[Pool]
        """

        poolelements = self.xml_findall("./pooled-inputs/pool")
        return [Pool(self.lims, p) for p in poolelements]

    def create_pool(self, name, samples):
        pool_root = self.xml_root.find("./pooled-inputs")
        pool_node = ETree.SubElement(pool_root, "pool", {"name": name})

        for sample in samples:
            ETree.SubElement(pool_node, "input", {"uri": sample.uri})


class AvailableInput(WrappedXml):
    def __init__(self, lims, xml_root):
        super(AvailableInput, self).__init__(lims, xml_root)

    replicates = attribute_property("replicates", types.NUMERIC, readonly=True)

    @property
    def input(self):
        """
        :type: Artifact
        """
        return self.lims.artifact_from_uri(self.xml_root.get("uri"))


class Placement(WrappedXml):
    container = subnode_link(Container, "location/container")  # type: Container
    location_value = subnode_property("location/value")  # type: str
    artifact = subnode_link(Artifact, ".", attributes=('uri',))  # type: Artifact


class StepPlacements(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/step}placements"

    step = subnode_link(Step, "step")  # type: Step
    placements = subnode_element_list(Placement, "output-placements", "output-placement")  # type: List[Placement]

    def __str__(self):
        # type: () -> string
        return "<Placements for Step %s>" % self.step.limsid

    @property
    def selected_containers(self):
        # type: () -> List[Container]
        """
        :type: list[Container]
        """

        selected_containers = self.xml_findall("./selected-containers/container")
        return self.lims.containers.from_link_nodes(selected_containers)

    def clear_selected_containers(self):
        # type: () -> None
        """
        Clears the list of selected containers associated with the step.
        This can be used to remove containers that are automatically
        created for the step when they are not used.
        """
        self.xml_root.remove(self.xml_root.find("./selected-containers"))
        ETree.SubElement(self.xml_root, "selected-containers")

    def add_selected_container(self, new_container):
        # type: (Container) -> None
        """
        Adds a new container to the step placement's list of selected containers.
        """

        selected_containers = self.xml_find("./selected-containers")
        ETree.SubElement(selected_containers, "container", {"uri": new_container.uri})

    def clear_placements(self):
        # type: () -> None
        """
        Clears all previous artifact placements recorded to this step.
        This is often called before starting automated placement to ensure
        that artifacts are not placed twice.
        """
        self.xml_root.remove(self.xml_root.find("./output-placements"))
        ETree.SubElement(self.xml_root, "output-placements")

    def create_placement(self, artifact, container, well_string):
        # type: (Artifact, Container, string) -> None
        """
        Place the provided artifact, in the provided container at the location
        described by the well_string.

        :param artifact: The artifact to place.
        :param container: The container that will hold the artifact.
        :param well_string: The location on the plate to place the artifact
        """
        placement_root = self.xml_root.find("./output-placements")
        placement_node = self.xml_root.find("./output-placements/output-placement[@uri='" + artifact.uri + "']")
        if not placement_node:
            placement_node = ETree.SubElement(placement_root, "output-placement", {"uri": artifact.uri})
        location_subnode = ETree.SubElement(placement_node, "location")
        ETree.SubElement(location_subnode, "container", {"uri": container.uri})
        ETree.SubElement(location_subnode, "value").text = well_string

    def create_placement_with_no_location(self, artifact):
        # type: (Artifact) -> None
        """
        Samples that are part of a process, but have been removed
        need to be included with out a location in some cases because
        Clarity will hold the old spot, which may now be used by another sample.
        """
        placement_root = self.xml_root.find("./output-placements")
        ETree.SubElement(placement_root, "output-placement", {"uri": artifact.uri})

    def commit(self):
        # type: () -> None
        """
        Push placement changes back to Clarity.
        """
        self.post_and_parse()


class Pool(WrappedXml):
    @property
    def name(self):
        # type: () -> str
        """
        :type: str
        """
        return self.xml_root.get("name")

    @lazy_property
    def inputs(self):
        # type: () -> List[Artifact]
        """
        :type: list[Artifact]
        """
        return [self.lims.artifacts.from_link_node(i) for i in self.xml_findall('./input')]

    @lazy_property
    def output(self):
        # type: () -> Artifact
        """
        :type: Artifact
        """
        node = self.xml_root
        return self.lims.artifacts.get(node.get("output-uri"), name=self.name)


class StepReagentLots(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/step}lots"

    def __init__(self, step, lims, uri):
        self.step = step
        super(StepReagentLots, self).__init__(lims, uri)

    def __str__(self):
        # type: () -> string
        return "<Reagent lots for Step %s>" % self.step.limsid

    def add_reagent_lots(self, elements):
        # type: (List[ReagentLot]) -> None
        """
        :param elements: Add reagent lots to the step
        :type elements: list[ReagentLot]
        """

        reagent_lots = self.xml_find("./reagent-lots")
        current_lots = [lot.uri for lot in self.reagent_lots]
        for element in elements:
            if element.uri not in current_lots:
                ETree.SubElement(reagent_lots, "reagent-lot", {"uri": element.uri})

    @property
    def reagent_lots(self):
        # type: () -> List[ReagentLot]
        """
        :type: list(ReagentLot)
        """

        reagent_elements = self.xml_findall("./reagent-lots/reagent-lot")
        return [ReagentLot(self.lims, p.get("uri")) for p in reagent_elements]


class StepProgramStatus(ClarityElement):
    """
    Manage the status of the currently executing step. By setting a
    message to the step status, a message box will be displayed to
    the user.

    The AI node will set the status to RUNNING, but does not
    allow the API to set this value.

    NOTE: A user has to action Step transition, upon message box display.
    i.e. There is no API request to get past the message box.
    In practise, using the 'program-status' endpoint conflicts with using StepRunner to develop automated workflow tests
    """
    UNIVERSAL_TAG = "{http://genologics.com/ri/step}program-status"

    step = subnode_link(Step, "step")  # type: Step

    message = subnode_property("message")  # type: string

    status = subnode_property("status")  # type: string

    def report_warning(self, message):
        # type: (string) -> None
        self.message = message
        self.status = "WARNING"
        self.commit()

    def report_ok(self, message):
        # type: (string) -> None
        self.message = message
        self.status = "OK"
        self.commit()

    def report_error(self, message):
        # type: (string) -> None
        self.message = message
        self.status = "ERROR"
        self.commit()

    def __str__(self):
        # type: () -> string
        return "<Program Status for Step %s>" % self.step.limsid


class StepTrigger(WrappedXml):

    def __init__(self, step, uri):
        self.step = step
        super(StepTrigger, self).__init__(step.lims, uri)

    @property
    def name(self):
        # type: () -> str
        """
        :type: str
        """
        return self.xml_root.get("name")

    def fire(self):
        # type: () -> None
        log.info("Firing script %s", self.name)
        self.lims.request("post", self.xml_root.get("uri"))
        self.step.wait_for_epp()


class StepReagents(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/step}reagents"

    def __init__(self, step, lims, uri):
        self.step = step
        super(StepReagents, self).__init__(lims, uri)

    def __str__(self):
        # type: () -> string
        return "<Reagent Placements for Step %s>" % self.step.limsid

    reagent_category = subnode_property("reagent-category")  # type: string

    @property
    def output_reagents(self):
        # type: () -> List[OutputReagent]
        """
        :type: list(OutputReagent)
        """
        nodes = self.xml_findall("./output-reagents/output")
        if nodes is None:
            return None

        return [OutputReagent(self, node) for node in nodes]


class OutputReagent(WrappedXml):
    def __init__(self, step, node):
        self.step = step
        super(OutputReagent, self).__init__(step.lims, node)

    @property
    def reagent_label(self):
        # type: () -> string
        """
        :type: str
        """
        node = self.xml_find('./' + "reagent-label")
        if node is None:
            return None
        return node.get("name")

    @reagent_label.setter
    def reagent_label(self, value):
        # type: (string) -> None

        node = self.xml_find('./' + "reagent-label")

        if node is None:
            node = ETree.SubElement(self.xml_root, "reagent-label")

        node.set("name", value)
