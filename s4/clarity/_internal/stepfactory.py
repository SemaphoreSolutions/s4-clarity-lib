# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from .factory import ElementFactory


class StepFactory(ElementFactory):
    def from_link_node(self, xml_node):
        """
        Override so that we can accept a process link or a step link.
        Requires that node include a limsid

        :rtype: ClarityElement
        """
        if xml_node is None:
            return None

        limsid = xml_node.get("limsid")
        if limsid:
            obj = self.from_limsid(limsid)
            name = xml_node.get("name")
            if name:
                obj._name = name
        else:
            obj = super(StepFactory, self).from_link_node(xml_node)

        return obj

    def _query_uri_and_tag(self):
        return self.lims.root_uri + "/processes", "process"

    def get_by_name(self, protocol_name, step_name):
        protocol = self.lims.protocols.get_by_name(protocol_name)
        step_config = protocol.step(step_name)
        if step_config is None:
            raise Exception("Step configuration for protocol %s and step %s could not be located." % (protocol_name, step_name))
        return step_config
