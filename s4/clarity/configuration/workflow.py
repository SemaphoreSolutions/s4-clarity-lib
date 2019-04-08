# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
from s4.clarity._internal.props import attribute_property
from s4.clarity import ClarityElement, lazy_property
from .stage import Stage
from s4.clarity.routing import Router


class Workflow(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/workflowconfiguration}workflow"

    PENDING_STATUS = "PENDING"
    ACTIVE_STATUS = "ACTIVE"
    ARCHIVED_STATUS = "ARCHIVED"

    status = attribute_property("status")

    @property
    def is_active(self):
        """
        :type: bool
        """
        return self.status == Workflow.ACTIVE_STATUS

    @property
    def is_pending(self):
        """
        :type: bool
        """
        return self.status == Workflow.PENDING_STATUS

    @property
    def is_archived(self):
        """
        :type: bool
        """
        return self.status == Workflow.ARCHIVED_STATUS

    @lazy_property
    def protocols(self, prefetch=True):
        """
        :param: prefetch: set to False if you don't want an automatic batch_get.
        :type: prefetch: bool

        :rtype: list[Protocol]
        """
        prots = self.lims.protocols.from_link_nodes(self.xml_findall("./protocols/protocol"))

        if prefetch:
            self.lims.protocols.batch_fetch(prots)

        return prots

    @property
    def stages(self):
        """
        :rtype: list[Stage]
        """
        return self.lims.stages.from_link_nodes(self.xml_findall("./stages/stage"))

    def stage_from_id(self, stageid):
        """
        :rtype: Stage or None
        """
        for stage in self.stages:
            if stage.uri.split('/')[-1] == stageid:
                return stage
        return None

    def enqueue(self, artifact_or_artifacts):
        """
        Add one or more artifacts to the start of the workflow

        :type: artifact_or_artifacts: Artifact | list[Artifact]
        """
        r = Router(self.lims)
        r.assign(self.uri, artifact_or_artifacts)
        r.commit()

    def remove(self, artifact_or_artifacts):
        """
        Remove one or more artifacts from the workflow

        :type: artifact_or_artifacts: Artifact | list[Artifact]
        """
        r = Router(self.lims)
        r.unassign(self.uri, artifact_or_artifacts)
        r.commit()
