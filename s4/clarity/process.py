# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import ClarityElement, FieldsMixin
from .iomaps import IOMapsMixin
from ._internal.props import subnode_link
from .researcher import Researcher


class Process(IOMapsMixin, FieldsMixin, ClarityElement):
    """
    :ivar list[IOMap] iomaps:
    :ivar list[Artifact] inputs:
    :ivar list[Artifact] outputs:
    :ivar list[Artifact] shared_outputs:

    :ivar str|None uri:
    :ivar LIMS lims:
    """
    UNIVERSAL_TAG = "{http://genologics.com/ri/process}process"
    ATTACH_TO_CATEGORY = "ProcessType"
    IOMAPS_XPATH = "input-output-map"
    IOMAPS_OUTPUT_TYPE_ATTRIBUTE = "output-type"

    technician = subnode_link(Researcher, "technician", readonly=True)  # type: Researcher

    @property
    def process_type(self):
        """:type: ProcessType"""
        return self.lims.process_types.from_link_node(self.xml_find("./type"))

    def _get_attach_to_key(self):
        return self.process_type.name, self.ATTACH_TO_CATEGORY

    def _get_iomaps_shared_result_file_type(self):
        return next((output.get('display-name') for output in self.process_type.outputs
                     if output.get('artifact-type') == 'ResultFile'
                     and output.get('output-generation-type') == 'PerAllInputs'), None)
