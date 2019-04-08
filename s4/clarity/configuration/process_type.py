# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import s4.clarity._internal
from s4.clarity import types
from s4.clarity._internal.props import subnode_property, subnode_property_list_of_dicts, subnode_link, subnode_links, attribute_property


class ProcessType(s4.clarity._internal.ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/processtype}process-type"

    inputs = subnode_property_list_of_dicts('process-input', as_attributes=["name"])

    outputs = subnode_property_list_of_dicts('process-output', as_attributes=["name", "uri"])

    parameters = subnode_property_list_of_dicts('parameter', as_attributes=["name"])

    def get_parameter(self, parameter_name):
        """
        :type parameter_name: str
        :param parameter_name: the name of the parameter to retrieve

        :rtype: dict
        """
        hits = list(filter(lambda p: p['name'] == parameter_name, self.parameters))
        if len(hits) > 1:
            raise Exception("more than one parameter named '%s' found" % parameter_name)
        elif hits:
            return hits[0]
        else:
            return None


class ProcessTemplate(s4.clarity._internal.FieldsMixin, s4.clarity._internal.ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/processtemplate}process-template"

    type = subnode_link(ProcessType, 'type', attributes=('uri',))

    is_default = subnode_property('is-default', types.BOOLEAN)



class Automation(s4.clarity._internal.ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/automation}automation"

    name = attribute_property('name')
    context = subnode_property('context')
    command_string = subnode_property('string')
    channel = subnode_property('channel')

    process_types = subnode_links(ProcessType, "process-type", "process-types")
