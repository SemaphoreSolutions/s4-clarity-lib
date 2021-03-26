# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import ClarityElement
from ._internal.props import subnode_property
from s4.clarity import types


class ControlType(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/controltype}control-type"

    supplier = subnode_property("supplier")
    catalogue_number = subnode_property("catalogue-number")
    website = subnode_property("website", types.URI)
    concentration = subnode_property("concentration")
    archived = subnode_property("archived", types.BOOLEAN)
    single_step = subnode_property("single-step", types.BOOLEAN)
