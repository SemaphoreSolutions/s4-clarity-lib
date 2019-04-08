# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
from __future__ import print_function
import logging
from collections import defaultdict

log = logging.getLogger(__name__)


def set_next_actions(epp, default_action=None, controls_action=None, failed_qc_action=None, action_func=None):
    """
    :type epp: s4.clarity.scripts.StepEPP
    :type action_func: (s4.clarity.Artifact) -> str
    :param failed_qc_action: applied to any sample or control that has failed qc.
    :param controls_action: applied to controls. if this is a qc step, only controls which have passed.
    :param action_func: called with each artifact; must return an action (string).
        if either failed_qc_action or controls_action are set, and also action_func is set, action_func will only
        be called for artifacts which are not caught by those actions.
        if action_func is None, or returns None for an artifact, the default is used.
    :param default_action: if None, an appropriate action is calculated (e.g. next step, or complete protocol.)
    """

    actions_list = epp.step.actions.next_actions

    auto_default_action, next_step_uri = _default_action_and_uri_for_step(epp.step)

    if default_action is None:
        default_action = auto_default_action
        log.debug("default action: %s" % default_action)

    changed = False

    need_full_artifact_fetch = action_func is not None or \
        failed_qc_action is not None or \
        controls_action is not None

    if need_full_artifact_fetch:
        artifact_uris = [action["artifact-uri"] for action in actions_list]
        epp.step.lims.artifacts.batch_get(artifact_uris)

    for action_for_artifact in actions_list:

        artifact = epp.step.lims.artifact_from_uri(action_for_artifact["artifact-uri"])

        if controls_action is not None and artifact.is_control:
            new_action = controls_action
        elif failed_qc_action is not None and artifact.qc_failed():
            new_action = failed_qc_action
        elif action_func is not None:
            new_action = action_func(artifact) or default_action
        else:
            new_action = default_action

        if new_action is None:
            # only possible if default_action is None
            log.info("SKIPPING %s: taking no action (leaving in step)", artifact)
            continue

        current_action = action_for_artifact.get("action")

        if current_action is None or current_action != new_action:
            action_for_artifact["action"] = new_action

            if new_action == "nextstep":
                action_for_artifact["step-uri"] = next_step_uri
            elif "step-uri" in action_for_artifact:
                del action_for_artifact["step-uri"]

            log.info("CHANGED %s: %s" % (artifact, new_action))
            changed = True
        else:
            log.info("UNCHANGED %s: %s" % (artifact, current_action))

    if changed:
        epp.step.actions.next_actions = actions_list
        epp.step.actions.commit()

    print("Next Actions Set Successfully")


def route_to_next_protocol(step, artifacts_to_route):
    """
    Queues the given artifacts directly to the first step of the next protocol.
    NOTE: Artifacts *must* be in-progress in the current step, or an exception will be thrown.

    :type step: step.Step
    :type artifacts_to_route: list[s4.clarity.Artifact]
    """

    # figure out how many workflow stages need to be skipped
    current_protocol_step_count = step.configuration.protocol.number_of_steps
    protocol_step_index = step.configuration.protocol_step_index
    steps_to_skip = int(current_protocol_step_count - protocol_step_index + 1)

    stages_to_artifacts = get_current_workflow_stages(step, artifacts_to_route)

    for current_stage, artifact_list in stages_to_artifacts.items():
        new_stage_index = int(current_stage.index) + steps_to_skip

        if new_stage_index > len(current_stage.workflow.stages):
            # This is the last protocol, so don't route the artifact.
            log.info("Artifacts with LIMS IDs \"%s\" are in the last protocol. Will not route." % ", ".join(artifact.limsid for artifact in artifact_list))
            continue

        new_stage_to_route_to = current_stage.workflow.stages[new_stage_index]
        new_stage_to_route_to.enqueue(artifact_list)


def get_current_workflow_stages(step, artifacts):
    """
    Given artifacts in a currently running step, finds their current workflow stages.

    :returns: a dict mapping workflow stages to lists of artifacts which are currently in them.
    :rtype: dict[Stage, list[Artifact]]
    """

    iomaps_output_keyed = step.details.iomaps_output_keyed()
    stage_to_artifacts = defaultdict(list)

    for artifact in artifacts:

        # Make sure to get the workflow stages from the input, as it may not be the artifact we're actually routing
        inputs = iomaps_output_keyed.get(artifact)
        if inputs:
            workflow_stages = get_artifact_workflow_stages_for_current_step(step, inputs[0])
        else:
            workflow_stages = get_artifact_workflow_stages_for_current_step(step, artifact)

        for workflow_stage in workflow_stages:
            stage_to_artifacts[workflow_stage].append(artifact)

    return stage_to_artifacts


def route_to_stage_by_name(step, artifacts_to_route, target_stage_name,
                           name_matches_base_name=lambda name, requested: name == requested):
    """
    Queues the given artifacts to the first stage in the artifact's workflow with the given name.
    NOTE: Artifacts *must* be in-progress in the current step, or an exception will be thrown.
    Optionally takes a name comparison function to use. Defaults to exact name matching.

    :type step: step.Step
    :type artifacts_to_route: list[s4.clarity.Artifact]
    :type target_stage_name: str
    :type name_matches_base_name: (str, str) -> bool
    """
    if len(artifacts_to_route) == 0:
        return

    stages_to_artifacts = get_current_workflow_stages(step, artifacts_to_route)

    for current_stage, artifact_list in stages_to_artifacts.items():
        found_stage = False
        workflow = current_stage.workflow

        for workflow_stage in workflow.stages:
            if name_matches_base_name(workflow_stage.name, target_stage_name):
                workflow_stage.enqueue(artifact_list)
                found_stage = True
                break

        if not found_stage:
            raise Exception("Unable to route artifacts (%s) to stage '%s' -- match not found in workflow." %
                            (artifact_list, target_stage_name))


def get_artifact_workflow_stages_for_current_step(step, artifact):
    workflow_stages = [stage_history.stage
                       for stage_history in artifact.workflow_stages
                       if stage_history.status == "IN_PROGRESS"
                       and stage_history.stage.step.uri == step.configuration.uri]

    if not workflow_stages:
        # The artifact is not in progress at the current step, so we can't determine which stage to route to.
        raise Exception("Can not retrieve an in-progress workflow stage for artifact '%s' in step '%s'." %
                        (artifact.name, step.name))

    return workflow_stages


def _default_action_and_uri_for_step(step):

    stepconf = step.configuration
    transitions = stepconf.transitions

    if transitions is None or len(transitions) == 0:
        if stepconf.protocol_step_index == stepconf.protocol.number_of_steps:
            action = "complete"
        else:
            action = "leave"

        next_step_uri = None

    else:
        action = "nextstep"
        next_step_uri = transitions[0]["next-step-uri"]

    return action, next_step_uri
