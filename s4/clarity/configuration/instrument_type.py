# Copyright 2025 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from s4.clarity._internal import ClarityElement
from s4.clarity._internal.props import subnode_links, subnode_property
from .process_type import ProcessType


class InstrumentType(ClarityElement):
    """
    Reference: https://d10e8rzir0haj8.cloudfront.net/latest/data_itp.html#element_instrument-type
    """

    UNIVERSAL_TAG = "{http://genologics.com/ri/instrumenttype}instrument-type"

    name = subnode_property("name")
    vendor = subnode_property("vendor")
    process_types = subnode_links(ProcessType, "process-type", "process-types")
