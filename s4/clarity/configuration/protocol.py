# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from s4.clarity._internal.element import ClarityElement, WrappedXml, BatchFlags
from s4.clarity.reagent_kit import ReagentKit
from s4.clarity.control_type import ControlType
from s4.clarity._internal.props import subnode_property_list_of_dicts, subnode_property, subnode_property_literal_dict, attribute_property, subnode_element_list
from s4.clarity import types, lazy_property


class Protocol(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/protocolconfiguration}protocol"
    BATCH_FLAGS = BatchFlags.QUERY
    REQUEST_PATH = '/configuration/protocols'

    properties = subnode_property_literal_dict('protocol-properties', 'protocol-property')
    index = attribute_property("index", typename=types.NUMERIC)

    @lazy_property
    def steps(self):
        """
        :type: list[StepConfiguration]
        """
        return [StepConfiguration(self, n) for n in self.xml_findall('./steps/step')]

    def _step_node(self, name):
        for n in self.xml_findall('./steps/step'):
            if n.get('name') == name:
                return n
        return None

    def step_from_id(self, stepid):
        """
        :rtype: StepConfiguration or None
        """
        for step in self.steps:
            if step.uri.split('/')[-1] == stepid:
                return step
        return None

    def step(self, name):
        """
        :rtype: StepConfiguration or None
        """
        for step in self.steps:
            if step.name == name:
                return step
        return None

    @property
    def number_of_steps(self):
        """
        :type: int
        """
        return len(self.steps)


class ProtocolStepField(WrappedXml):
    name = attribute_property("name")
    style = attribute_property("style")
    attach_to = attribute_property("attach-to")


class StepConfiguration(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/protocolconfiguration}step"

    def __init__(self, protocol, node):
        """
        :type protocol: Protocol
        """
        super(StepConfiguration, self).__init__(protocol.lims, uri=None, xml_root=node)
        self.protocol = protocol

    properties = subnode_property_literal_dict('step-properties', 'step-property')
    protocol_step_index = subnode_property("protocol-step-index", types.NUMERIC)
    queue_fields = subnode_element_list(ProtocolStepField, "queue-fields", "queue-field")
    step_fields = subnode_element_list(ProtocolStepField, "step-fields", "step-field")
    sample_fields = subnode_element_list(ProtocolStepField, "sample-fields", "sample-field")
    triggers = subnode_property_list_of_dicts('epp-triggers/epp-trigger', as_attributes=[
        'status', 'point', 'type', 'name'
    ])
    transitions = subnode_property_list_of_dicts('transitions/transition', as_attributes=[
        'name', 'sequence', 'next-step-uri'
    ], order_by=lambda x: int(x.get('sequence')))
    
    def refresh(self):
        """
        :raise Exception: Unable to refresh step directly, use protocol
        """
        # FIXME?
        raise Exception("Unable to refresh step directly, use protocol")

    def put_and_parse(self, alternate_uri=None):
        self.protocol.put_and_parse(alternate_uri)

    def post_and_parse(self, alternate_uri=None):
        self.protocol.post_and_parse(alternate_uri)

    @lazy_property
    def process_type(self):
        """
        :type: ProcessType
        """
        pt_display_name = self.get_node_text('process-type')

        results = self.lims.process_types.query(displayname=pt_display_name)
        if results:
            return results[0]
        else:
            raise Exception("Process type '%s' not found in Clarity", pt_display_name)

    @lazy_property
    def required_reagent_kits(self):
        """
        :type: ReagentKit
        """
        reagent_kits = self.xml_findall("./required-reagent-kits/reagent-kit")
        return [ReagentKit(self.lims, p.get("uri")) for p in reagent_kits]

    @lazy_property
    def permitted_control_types(self):
        """
        :type: ControlType
        """
        control_types = self.xml_findall("./permitted-control-types/control-type")
        return [ControlType(self.lims, p.get("uri")) for p in control_types]

    @lazy_property
    def queue(self):
        """
        :type: Queue
        """
        return self.lims.queues.from_limsid(self.limsid)
