# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
from s4.clarity.researcher import Researcher
from s4.clarity.reagent_kit import ReagentKit
from s4.clarity.container import ContainerType
from s4.clarity import types
from s4.clarity._internal import ClarityElement, FieldsMixin, WrappedXml
from s4.clarity._internal.props import subnode_property, subnode_link, subnode_links, attribute_property, subnode_element_list, subnode_element
from s4.clarity.configuration.udf import Udf, Field


class ProcessInput(WrappedXml):
    """
    Represents a process-input in Clarity

    https://www.genologics.com/files/permanent/API/latest/data_ptp.html#process-input
    """

    artifact_type = subnode_property('artifact-type')
    display_name = subnode_property('display-name')
    remove_working_flag = subnode_property('remove-working-flag', typename=types.BOOLEAN)


class ProcessOutput(WrappedXml):
    """
    Represents a process-output in Clarity

    https://www.genologics.com/files/permanent/API/latest/data_ptp.html#process-output
    """

    artifact_type = subnode_property('artifact-type')
    display_name = subnode_property('display-name')
    output_generation_type = subnode_property('output-generation-type')
    number_of_outputs = subnode_property('number-of-outputs', typename=types.NUMERIC)
    output_name = subnode_property('output-name')
    assign_working_flag = subnode_property('assign-working-flag', typename=types.BOOLEAN)
    field_definitions = subnode_links(Udf, 'field-definition')


class Parameter(WrappedXml):
    """
    Represents a parameter in Clarity

    https://www.genologics.com/files/permanent/API/latest/data_ptp.html#parameter
    """

    name = attribute_property('name')
    command_string = subnode_property('string')
    run_program_per_event = subnode_property('run-program-per-event', typename=types.BOOLEAN)
    channel = subnode_property('channel')
    invocation_type = subnode_property('invocation-type')
    # ToDo: add file list


class QueueField(Field):
    """
    Represents a queuefield in Clarity

    https://www.genologics.com/files/permanent/API/latest/data_ptp.html#queuefield
    """

    detail = attribute_property('detail')


class IceBucketField(Field):
    """
    Represents a icebucketfield in Clarity

    https://www.genologics.com/files/permanent/API/latest/data_ptp.html#icebucketfield
    """

    detail = attribute_property('detail')


class ProcessTypeAttribute(WrappedXml):
    """
    Represents a process-type-attribute in Clarity

    https://www.genologics.com/files/permanent/API/latest/data_ptp.html#process-type-attribute
    """

    name = attribute_property('name')
    value = subnode_property(".")


class ProcessStepProperty(WrappedXml):
    """
    Represents a step-property in Clarity

    https://www.genologics.com/files/permanent/API/latest/data_ptp.html#step-property
    """

    name = attribute_property('name')
    value = attribute_property('value')


class ProcessEppTrigger(WrappedXml):
    """
    Represents an epp-trigger in Clarity

    https://www.genologics.com/files/permanent/API/latest/data_ptp.html#epp-trigger
    """

    name = attribute_property('name')
    status = attribute_property('status')
    point = attribute_property('point')
    type = attribute_property('type')

class ProcessPermittedInstrumentType(WrappedXml):
    """
    Represents an Instrument Type definition in the Process type.

    This field is a string.
    """

    instrument_type = subnode_property('.')

class ProcessType(ClarityElement):
    """
    Represents a process-type in Clarity

    https://www.genologics.com/files/permanent/API/latest/data_ptp.html#element_process-type
    """

    UNIVERSAL_TAG = "{http://genologics.com/ri/processtype}process-type"

    field_definitions = subnode_links(Udf, 'field-definition')
    input = subnode_element(ProcessInput, 'process-input')
    outputs = subnode_element_list(ProcessOutput, '.', 'process-output')
    parameters = subnode_element_list(Parameter, '.', 'parameter')
    process_type_attributes = subnode_element_list(ProcessTypeAttribute, '.', 'process-type-attribute')
    required_reagent_kits = subnode_links(ReagentKit, 'reagent-kit', 'required-reagent-kits')
    permitted_instrument_types = subnode_element_list(ProcessPermittedInstrumentType, 'permitted-instrument-types', 'instrument-type')
    permitted_containers = subnode_links(ContainerType, 'container-type', 'permitted-containers')
    queue_fields = subnode_element_list(QueueField, 'queue-fields', 'queue-field')
    ice_bucket_fields = subnode_element_list(QueueField, 'ice-bucket-fields', 'ice-bucket-field')
    step_fields = subnode_element_list(Field, 'step-fields', 'step-field')
    sample_fields = subnode_element_list(Field, 'sample-fields', 'sample-field')
    step_properties = subnode_element_list(ProcessStepProperty, 'step-properties', 'step-property')
    epp_triggers = subnode_element_list(ProcessEppTrigger, 'epp-triggers', 'epp-trigger')

    def get_parameter(self, parameter_name):
        """
        Returns the Parameter with the provided name, or None.
        :param parameter_name: Name of parameter to look for
        :type parameter_name: str
        :return The Parameter, or None
        :rtype Parameter
        """
        matching_param = [p for p in self.parameters if p.name == parameter_name]
        if len(matching_param) > 1:
            raise Exception("more than one parameter named '%s' found" % parameter_name)
        elif matching_param:
            return matching_param[0]
        else:
            return None


class ProcessTemplate(FieldsMixin, WrappedXml):
    """
    Represents a process-template in Clarity.

    https://www.genologics.com/files/permanent/API/latest/data_ptm.html#element_process-template
    """

    UNIVERSAL_TAG = "{http://genologics.com/ri/processtemplate}process-template"

    type = subnode_link(ProcessType, 'type', attributes=('uri',))
    technician = subnode_link(Researcher, 'technician', attributes=('uri',))
    is_default = subnode_property('is-default', types.BOOLEAN)


class Automation(ClarityElement):
    """
    Represents an automation in Clarity.

    https://www.genologics.com/files/permanent/API/latest/data_aut.html#element_automation
    """

    UNIVERSAL_TAG = "{http://genologics.com/ri/automation}automation"

    name = attribute_property('name')
    context = subnode_property('context')
    command_string = subnode_property('string')
    channel = subnode_property('channel')

    process_types = subnode_links(ProcessType, "process-type", "process-types")
