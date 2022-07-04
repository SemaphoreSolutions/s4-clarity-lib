# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
from s4.clarity._internal.props import attribute_property
from s4.clarity import ClarityElement, lazy_property
from s4.clarity.routing import Router


class Stage(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/workflow}stage"

    index = attribute_property("index")

    @lazy_property
    def workflow(self):
        """
        :type: Workflow
        """
        return self.lims.workflows.from_link_node(self.xml_find("./workflow"))

    @lazy_property
    def protocol(self):
        """
        :type: Protocol
        """
        return self.lims.protocols.from_link_node(self.xml_find("./protocol"))

    @lazy_property
    def step(self):
        """
        :type: StepConfiguration
        """
        step_node = self.xml_find("step")
        if step_node is not None:
            return self.lims.stepconfiguration_from_uri(step_node.get("uri"))
        else:
            return None

    def enqueue(self, artifact_or_artifacts):
        """
        Add one or more artifacts to the stage's queue

        :param artifact_or_artifacts: The artifact(s) to enqueue
        :type artifact_or_artifacts: s4.clarity.Artifact | list[s4.clarity.Artifact]
        """
        r = Router(self.lims)
        r.assign(self.uri, artifact_or_artifacts)
        r.commit()

    def remove(self, artifact_or_artifacts):
        """
        Remove one or more sample artifacts from the stage

        :param artifact_or_artifacts: The artifact(s) to enqueue
        :type artifact_or_artifacts: s4.clarity.Artifact | list[s4.clarity.Artifact]
        """
        r = Router(self.lims)
        r.unassign(self.uri, artifact_or_artifacts)
        r.commit()
