# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import abc
import functools
import time
import logging

from s4.clarity import ETree, lazy_property
from s4.clarity.step import Step
from s4.clarity import ClarityException

log = logging.getLogger(__name__)

CONTAINER_TYPE_TUBE = "Tube"

# Step States, each one representing a window in a step
PLACEMENT_STATE = "Placement"
ARRANGING_STATE = "Arranging"
STARTED_STATE = "Started"
SETUP_STATE = "Step Setup"
POOLING_STATE = "Pooling"
ADD_REAGENT_STATE = "Add Reagent"
RECORD_DETAILS_STATE = "Record Details"
ASSIGN_NEXT_STEPS_STATE = "Assign Next Steps"
COMPLETED_STATE = "Completed"

ALL_STEP_STATES = [PLACEMENT_STATE,
                   ARRANGING_STATE,
                   STARTED_STATE,
                   SETUP_STATE,
                   POOLING_STATE,
                   ADD_REAGENT_STATE,
                   RECORD_DETAILS_STATE,
                   ASSIGN_NEXT_STEPS_STATE,
                   COMPLETED_STATE]


class StepRunner:
    """
    StepRunner is the abstract class that provides base functionality to automatically execute a step in Clarity.
    Sub classes can implement 'virtual' methods to take custom action at each screen in the step.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, lims, protocolname, stepconfigname, usequeuedinputs=True, numberofinputs=4):
        self.step = None

        self.lims = lims
        if self.lims is None:
            raise StepRunnerException("lims is a required parameter and may not be None")

        self.protocolname = protocolname
        if self.protocolname is None:
            raise StepRunnerException("protocolname is a required parameter and may not be None")

        self.stepconfigname = stepconfigname
        if self.stepconfigname is None:
            raise StepRunnerException("stepconfigname is a required parameter and may not be None")

        self.usequeuedinputs = usequeuedinputs
        self.numberofinputs = numberofinputs

        self.timeformat = "%I:%S %p"  # HH:MM am/pm

    @lazy_property
    def step_config(self):
        """
        :type: StepConfiguration
        """
        try:
            protocol_config = self.lims.protocols.get_by_name(self.protocolname)
            step = protocol_config.step(self.stepconfigname)
        except ClarityException as ex:
            log.error("StepRunner could not load step configuration: %s" % str(ex))
            raise Exception("Configuration for step %s in protocol %s could not be located." % (self.stepconfigname, self.protocolname))

        if step is None:
            raise StepRunnerException("Unable to load step with name %s from protocol %s." % (self.stepconfigname, self.protocolname))

        return step

    ################################
    # Virtual Methods
    # The following methods are overridden in sub classes to provide
    # stage specific functionality
    ################################

    def replicates_for_control(self, control):
        # Override to generate a custom number of replicates for each control.
        return 1

    def replicates_for_inputuri(self, input_uri):
        # Override to generate a custom number of replicates for each sample.
        return 1

    def setup(self):
        # Override this method to implement actions on the step setup screen.
        pass

    def placement(self):
        # Override this method to implement actions on the placement screen.
        pass

    def arranging(self):
        # Override this method to implement actions on the arrangement screen.
        pass

    def pooling(self):
        # Override this method to implement actions on the pooling screen.
        pass

    def add_reagents_step(self):
        # Override this method to implement actions on the add reagent screen.
        pass

    def record_details(self):
        # Override this method to implement actions on the record details screen.
        pass

    def next_steps(self):
        # Override this method to implement actions on the next steps screen.
        pass

    ################################
    # End Virtual Methods
    ################################

    def _run_setup(self):
        # Runs the Step Setup phase
        log.info("Starting Step Setup Phase")
        self.setup()
        self.step.advance()

    def _run_placement(self):
        # Runs the placement phase
        log.info("Starting Placement Phase")
        self.placement()
        self.step.advance()

    def _run_arranging(self):
        # Runs the Arranging phase
        log.info("Starting Arranging Phase")
        self.arranging()
        # Note: Most versions of Clarity do not support advancing from the Arranging state.

    def _run_pooling(self):
        # Runs the Pooling phase
        log.info("Starting Pooling Phase")
        self.pooling()
        self.step.advance()

    def _run_add_reagent(self):
        # Runs the Add Reagent phase
        log.info("Starting Add Reagent Phase")
        self.add_reagents_step()
        self.step.advance()

    def _run_record_details(self):
        # Runs the Record Details phase
        log.info("Starting Record Details Phase")
        self.record_details()
        self.step.advance()

    def _run_next_steps(self):
        # Runs the Assign Next Steps phase
        log.info("Starting Assign Next Steps Phase")
        self.next_steps()
        self.step.advance()

    def load_existing_step(self, step_limsid):
        """
        Loads an existing step from Clarity into the StepRunner.
        :param step_limsid: The LIMS ID of an existing, but not completed step.
        """
        self.step = self.lims.step(step_limsid)

        log.info("%s is starting previously created step %s" % (self.__class__.__name__, self.step.uri))

        self._wait_on_started()

    def load_new_step(self, input_uri_list=None, previous_step=None, controls=None, container_type=None, reagent_type=None, control_names=None):
        """
        Starts a new step to be used by the StepRunner.

        :param input_uri_list:  A list of artifacts that will be use to run the step
        :param previous_step: A step that has already run, the outputs of which will be used as the inputuris
        :param controls: The list of controls that will be included in this step
        :param container_type: The container that output artifacts will be placed in. If none is supplied the default will be used.
        :param reagent_type: The name of the reagent category to use for the step. If none is supplied the default will be used.
        :param control_names: If no controls are provided, this list of control names will be used to look up controls and include them in the step
        """

        # Make sure the user knows that we are ignoring some of their input
        if input_uri_list is not None and previous_step is not None:
            raise StepRunnerException("Steps can not be started with both an input uri list and a previous step.")

        # If there is no input uri list,
        if input_uri_list is None and previous_step is not None:
            log.info("Using artifacts from previously executed step %s %s" % (previous_step.name, previous_step.uri))
            input_uri_list = self.get_previous_steps_outputs(previous_step)

        if input_uri_list is None:
            if not self.usequeuedinputs:
                if not controls and not control_names:
                    raise StepRunnerException("No inputs provided and usequeuedinputs is false and no controls for %s" % self)
            else:
                log.info("Pulling existing artifacts from step queue.")
                input_uri_list = self._get_inputs_from_queue()

        if controls is None and control_names:
            controls = self.get_controls_from_control_names(control_names)

        self.step = self._new_step_from_configuration(input_uri_list, controls, container_type, reagent_type)

        self._wait_on_started()

    def _wait_on_started(self):
        """
        The started state happens when Clarity has accepted the request to create a new Step, but
        is in the process of starting it. This can happen on slow machines, or if there is a long EPP on step starting
        """
        while self.step.current_state == "Started":
            if self.step.program_status.status == 'ERROR':
                raise StepRunnerException("EPP failure while waiting for step to start: %s" % self.step.program_status.message)

            log.info("Waiting 1 second for auto-started step to begin.")
            time.sleep(1)
            self.step.refresh()
            self.step.program_status.refresh()

    def run(self, inputuris=None, previousstep=None, controls=None, containertype=None, reagenttype=None, steplimsid=None, control_names=None):
        """
        Runs a step from its current state to completion.

        :param inputuris: A list of artifacts that will be use to run the step
        :param previousstep: A step that has already run, the outputs of which will be used as the inputuris
        :param controls: The list of controls that will be included in this step
        :param containertype: The container that output artifacts will be placed in. If none is supplied the default will be used.
        :param reagenttype: The name of the reagent category to use for the step. If none is supplied the default will be used.
        :param steplimsid: The LIMS ID of an existing, but not completed step. If this is provided all other arguments will be ignored
        :param control_names: If no controls are provided, this list of control names will be used to look up controls and include them in the step
        """

        # Make sure that we are not passing in a bunch of stuff that is getting ignored.
        if steplimsid is not None and any([previousstep, controls, containertype, reagenttype, control_names]):
            raise StepRunnerException("If steplimsid is provided all other arguments are ignored. Please review your step runner script.")

        if steplimsid is not None:
            self.load_existing_step(steplimsid)
        else:
            self.load_new_step(inputuris, previousstep, controls, containertype, reagenttype, control_names)

        # Run to the end of the step
        self.run_to_state(COMPLETED_STATE)

        # Reload step state from the server
        self.step.refresh()

    def run_to_state(self, goal_state_name):
        """
        Execute sequential stages in the step until the goal state is reached.

        :param goal_state_name: The name of the state to run to, name must be in the list ALL_STEP_STATES list
        """
        # Either load_existing_step or load_new_step must be called before this
        if self.step is None:
            raise StepRunnerException("A step must be loaded before run_to_state may be called.")

        if goal_state_name not in ALL_STEP_STATES:
            raise StepRunnerException("Invalid goal state: %s" % goal_state_name)

        state_map = {
            PLACEMENT_STATE: self._run_placement,
            ARRANGING_STATE: self._run_arranging,
            STARTED_STATE: self._wait_on_started,
            SETUP_STATE: self._run_setup,
            POOLING_STATE: self._run_pooling,
            ADD_REAGENT_STATE: self._run_add_reagent,
            RECORD_DETAILS_STATE: self._run_record_details,
            ASSIGN_NEXT_STEPS_STATE: self._run_next_steps
        }

        previous_state = ""
        while self.step.current_state != goal_state_name:
            current_state = self.step.current_state

            if current_state == previous_state:
                raise StepRunnerException("Step has not advanced past state %s" % current_state)

            if current_state == COMPLETED_STATE:
                raise StepRunnerException("Step Completed before reaching state %s" % goal_state_name)

            next_state_function = state_map.get(current_state)
            if next_state_function is None:
                raise StepRunnerException("Step state '%s' was not in state map." % current_state)

            # Execute the script for the state
            next_state_function()

            previous_state = current_state

    def post_tube_to_tube(self, container_type_name=CONTAINER_TYPE_TUBE):
        """
        Create single-well (tube) containers, and place the outputs in them.

        This works around a 'bug' in Clarity where, when a step is run through the API, Clarity will not
        automatically move artifacts from input tubes to output tubes.

        It is necessary if you are automating a step that has tube inputs and tube outputs. Override the
        record_details() method in your sub class and call this method as the first action in it.

        @param container_type_name: the name of the container type. Must be single-well, but not necessarily "Tube"
        """
        container_type = self.lims.container_types.get_by_name(container_type_name)

        if not container_type:
            raise Exception("Container type '%s' can not be found. Please check your configuration." %
                            container_type_name)

        if not container_type.is_tube:
            raise Exception("The post_tube_to_tube method can only be called with tube-like containers.")

        self.step.placements.clear_placements()
        self.step.placements.clear_selected_containers()

        new_containers = self.lims.containers.batch_create(
            [self.lims.containers.new(name=output.limsid, container_type=container_type)
             for output in self.step.details.outputs]
        )

        for index, output in enumerate(self.step.details.outputs):
            self.step.placements.create_placement(output, new_containers[index], container_type.row_major_order_wells()[0])

        self.step.placements.post_and_parse()
        self.step.refresh()

    def add_default_reagents(self):
        """
        For every required reagent kit in the step, the first active lot
        will be selected. If there are no active lots it will be omitted.

        Archived kits will be ignored on Clarity 6.1 (api revision 32) and later.
        """
        revision = int(self.lims.current_minor_version[1:])
        log.info("Adding default reagent lots.")
        lots = []
        for kit in self.step.configuration.required_reagent_kits:
            if revision >= 32 and kit.archived:
                continue
            for lot in kit.related_reagent_lots:
                if lot.status == "ACTIVE":
                    lots.append(lot)
                    break
            else:
                log.warning("Reagent Kit %s has no active lots." % kit.name)

        if len(lots) > 0:
            self.step.reagent_lots.add_reagent_lots(lots)
            self.step.reagent_lots.commit()

    def get_previous_steps_outputs(self, previous_step, get_all=False):
        """
        By default, filters previous step's actioned artifacts which either continued to this step, or ended a protocol.
        If get_all=True, doesn't filter.

        :returns: list of artifact URIs that match the conditions
        :rtype: list[str]
        """
        if not previous_step:
            raise StepRunnerException("Unable to get previous step artifacts with out a previous step.")

        artifact_actions = previous_step.actions.artifact_actions

        if get_all:
            def filterfunc(aa):
                return True
        else:
            def filterfunc(aa):
                return (aa.action == "nextstep" and aa.step_uri == self.step_config.uri) or aa.action == "complete"

        return [aa.artifact_uri for aa in filter(filterfunc, list(artifact_actions.values()))]

    def get_started_step(self, previous_step, project_name):
        return previous_step.automatic_next_step.limsid

    def _new_step_from_configuration(self, input_uri_list, controls, containertype, reagenttype):
        """
        Creates a new step in clarity.

        :param input_uri_list: A list of artifacts that will be use to run the step
        :param controls: The list of controls that will be included in this step
        :param containertype: The container that output artifacts will be placed in.
        :param reagenttype: The name of the reagent category to use for the step.
        """
        log.info("Creating %s (user: %s)", self.__class__.__name__, self.lims.username)

        if not input_uri_list and not controls:
            raise StepRunnerException("Unable to create new step with no input artifacts or contols.")

        root = ETree.Element("{http://genologics.com/ri/step}step-creation")
        ETree.SubElement(root, "configuration", {'uri': self.step_config.uri})

        inputsnode = ETree.SubElement(root, "inputs")

        if input_uri_list:
            for input_uri in input_uri_list:
                attrib = {
                    'uri': input_uri,
                    'replicates': str(self.replicates_for_inputuri(input_uri))
                }
                ETree.SubElement(inputsnode, "input", attrib)

        if controls:
            for control in controls:
                attrib = {
                    'control-type-uri': control.uri,
                    'replicates': str(self.replicates_for_control(control))
                }
                ETree.SubElement(inputsnode, "input", attrib)

        if containertype is None:
            permitted_containers = self.step_config.xml_find("./permitted-containers")
            if permitted_containers is not None and len(permitted_containers) > 0:
                containertype = permitted_containers[0].text

        if containertype is not None:
            node = ETree.SubElement(root, "container-type")
            node.text = containertype
        else:
            log.warning("No container type specified for step.")

        if reagenttype is None:
            permitted_reagents = self.step_config.xml_find("./permitted-reagent-categories")
            if permitted_reagents is not None and len(permitted_reagents) > 0:
                reagenttype = permitted_reagents[0].text

        if reagenttype is not None:
            node = ETree.SubElement(root, "reagent-category")
            node.text = reagenttype

        step_xml_root = self.lims.request("post", self.lims.root_uri + "/steps", root)
        step = Step(self.lims, uri=step_xml_root.get("uri"), xml_root=step_xml_root, limsid=step_xml_root.get("limsid"))

        log.info("%s started step %s" % (self.__class__.__name__, step.uri))

        step.wait_for_epp()


        return step

    def _get_inputs_from_queue(self):
        step_id = self.step_config.uri.split("/")[-1]
        inputlist = self.lims.queues.from_limsid(step_id).queued_artifacts
        if len(inputlist) < self.numberofinputs:
            raise Exception("Too few inputs to push through step")
        return [input.uri for input in inputlist[0:self.numberofinputs]]

    def get_controls_from_control_names(self, candidate_control_names):
        """
        get control els controls from array of control_names
        :raise Exception: If any control names not permitted or non-existent
        """

        if candidate_control_names is None or not isinstance(candidate_control_names, list):
            raise StepRunnerException("Control names must be passed as a list.")

        if len(candidate_control_names) == 0:
            raise StepRunnerException("Unable to get controls for empty list of control names.")

        # Turn the control names into a set for faster lookups
        candidate_control_names = set(candidate_control_names)

        # Get a list of all valid controls
        controls = [permitted_control for permitted_control
                    in self.step_config.permitted_control_types
                    if permitted_control.name in candidate_control_names]

        # any control names not found in permitted control names are illegal
        if len(candidate_control_names) > len(controls):

            # Prepare a list of controls that are invalid
            valid_control_names = map(lambda c: c.name, controls)
            invalid_control_names = candidate_control_names - set(valid_control_names)

            # Warn user
            invalid_control_string = ", ".join(invalid_control_names)
            raise StepRunnerException("Control(s) '%s' not permitted in step config" % invalid_control_string)

        return controls

    def fire_script(self, script_name):
        parse_xls_script = next((program for program in self.step.available_programs if program.name == script_name),
                                None)
        if parse_xls_script:
            log.info("Running manual EPP '%s'" % script_name)
            parse_xls_script.fire()
        else:
            raise Exception("No EPP defined matching name '%s'" % script_name)

    def set_step_udf_as_user(self, udf_name, value, stop_on_error=True):
        """
        Set a Step UDF after first validating that it's both visible on the step, and editable.
        
        :param udf_name: Name of the udf
        :param value: Value to set
        :param stop_on_error: Whether to raise an Exception if the user couldn't set the value. Otherwise, the method
            will log an error and continue
        :raise Exception: If stop_on_error is True, and there is any reason that would prevent the user from setting the
            UDF in the Clarity UI
        """
        error_partials = []
        udf_config = self.step.details.get_udf_config(udf_name)

        if not udf_config.is_editable:
            error_partials.append("the UDF is not configured to be editable on the process type")

        step_field_visible = any(step_field.name == udf_name for step_field in self.step_config.step_fields)

        if not step_field_visible:
            error_partials.append("the UDF is not configured to be visible in the '%s' protocol."
                          % self.step.configuration.protocol.name)

        if error_partials:
            error_message = "StepRunner can not set the '%s' Step UDF on step '%s' as a user: %s." \
                            % (udf_name, self.step.name, ", and ".join(error_partials))

            if stop_on_error:
                raise Exception(error_message)
            else:
                log.error(error_message)

        self.step.details[udf_name] = value

    def set_artifact_udf_as_user(self, artifact, udf_name, value, stop_on_error=True):
        """
        Set an Artifact UDF after first validating that it's both visible on the step, and editable.

        :param artifact: An Artifact (Analyte or ResultFile) in a running step.
        :type artifact: s4.clarity.Artifact
        :param udf_name: Name of the udf
        :param value: Value to set
        :param stop_on_error: Whether to raise an Exception if the user couldn't set the value. Otherwise, the method
            will log an error and continue
        :raise Exception: If stop_on_error is True, and there is any reason that would prevent the user from setting the
            UDF in the Clarity UI
        """
        error_partials = []
        udf_config = artifact.get_udf_config(udf_name)
        artifact_type = artifact.type

        # Input UDFs may be displayed on a step with a ResultFile output, but they can not edited.
        if artifact in self.step.details.inputs:
            error_partials.append("users are not able to edit UDFs on step inputs")

        if not udf_config.is_editable:
            error_partials.append("the UDF is not configured to be editable")

        sample_field_visible = any(sample_field.name == udf_name and sample_field.attach_to == artifact_type
                                   for sample_field in self.step_config.sample_fields)

        if not sample_field_visible:
            error_partials.append("the UDF is not configured to be visible on the step")

        if error_partials:
            error_message = "StepRunner can not set %s UDF '%s' on Step '%s' as a user: %s." \
                            % (artifact_type, udf_name, self.step.name, ", and ".join(error_partials))

            if stop_on_error:
                raise Exception(error_message)
            else:
                log.error(error_message)

        artifact[udf_name] = value

    def prefetch_artifacts(self):
        """
        Loads the current state in Clarity of all inputs and outputs.
        """
        self.lims.artifacts.batch_refresh(self.step.details.inputs + self.step.details.outputs)


class StepRunnerException(Exception):
    pass


