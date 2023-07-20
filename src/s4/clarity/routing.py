# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
import logging
from collections import defaultdict
from s4.clarity import ETree

log = logging.getLogger(__name__)

ACTION_ASSIGN = "assign"
ACTION_UNASSIGN = "unassign"


class Router(object):
    """
    Class allowing routing of multiple artifacts to a given workflow or stage
    """
    def __init__(self, lims):
        self.lims = lims
        self.routing_dict = defaultdict(lambda:defaultdict(set))

    def clear(self):
        """
        Clears the routing node and the routing dict.
        """
        self.routing_dict = defaultdict(lambda:defaultdict(set))

    def remove(self, artifact_or_artifacts):
        """
        Remove given artifact or artifacts from the routing dict.
        No error is raised if the artifact is not found.
        """
        for artifact in self._normalize_as_list(artifact_or_artifacts):
            for routes in self.routing_dict.values():
                for artifact_set in routes.values():
                    artifact_set.discard(artifact)

    def assign(self, workflow_or_stage_uri, artifact_or_artifacts):
        """
        Stages an artifact or multiple artifacts to be assigned to a workflow_or_stage_uri.

        :type workflow_or_stage_uri: str
        :param workflow_or_stage_uri: The uri of either a workflow or workflow-stage. If a workflow uri is provided,
            the artifacts will be queued to the first stage. Otherwise, they will be queued to the specific workflow-stage.
        :type artifact_or_artifacts: s4.clarity.Artifact | list[s4.clarity.Artifact]
        """

        self._update_routing_dict(ACTION_ASSIGN, workflow_or_stage_uri, artifact_or_artifacts)

    def unassign(self, workflow_or_stage_uri, artifact_or_artifacts):
        """
        Stages an artifact or multiple artifacts to be unassigned from a workflow_or_stage_uri.

        :type workflow_or_stage_uri: str
        :param workflow_or_stage_uri: The uri of either a workflow or workflow-stage. If a workflow uri is provided,
            the artifacts will be removed from any stages of that workflow. Otherwise, they will be removed from the
            specified workflow stage.
        :type artifact_or_artifacts: s4.clarity.Artifact | list[s4.clarity.Artifact]
        """
        self._update_routing_dict(ACTION_UNASSIGN, workflow_or_stage_uri, artifact_or_artifacts)

    def _update_routing_dict(self, action, uri, artifact_or_artifacts):
        """
        Stages an artifact or multiple artifacts to be assigned to /unassigned from a workflow_or_stage_uri.

        :type action: str
        :param action: either "assign" or "unassign"
        :type uri: str
        :param uri: The uri of either a workflow or workflow-stage.
        """

        self.routing_dict[action][uri].update(
                self._normalize_as_list(artifact_or_artifacts)
            )

    def commit(self):
        """
        Generates the routing XML for workflow/stage assignment/unassignment and posts it.
        """
        routing_node = self._create_routing_node()
        self.lims.request("post", self.lims.root_uri + "/route/artifacts", routing_node)

    def _create_routing_node(self):
        """
        Generates the XML for  workflow/stage assignment/unassignment
        """
        routing_node = ETree.Element("{http://genologics.com/ri/routing}routing")
        for action, routes in self.routing_dict.items():
            for workflow_or_stage_uri, artifact_set in routes.items():
                if artifact_set:
                    assign_node = self._add_action_subnode(routing_node, action, workflow_or_stage_uri)
                    # create an artifact assign node for each samples
                    for artifact in artifact_set:
                        ETree.SubElement(assign_node, "artifact", {"uri": artifact.uri})

        return routing_node

    def _add_action_subnode(self, routing_node, action, workflow_or_stage_uri):
        """
        Generates a ElementTree.SubElement according to the action (assign / unassign) and the workflow/stage uri
        """
        if '/stages/' in workflow_or_stage_uri:
            assign_node = ETree.SubElement(routing_node, action, {'stage-uri': workflow_or_stage_uri})
        else:
            assign_node = ETree.SubElement(routing_node, action, {'workflow-uri': workflow_or_stage_uri})

        return assign_node

    def _normalize_as_list(self, artifact_or_artifacts):
        """
        Returns a list of artifacts from one or many artifacts
        """
        if not isinstance(artifact_or_artifacts, (list, set)):
            artifacts = [artifact_or_artifacts]
        else:
            artifacts = artifact_or_artifacts
        return artifacts

