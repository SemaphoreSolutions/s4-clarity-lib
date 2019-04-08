# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import ClarityElement
from ._internal.props import subnode_property, subnode_link
from .reagent_kit import ReagentKit
from s4.clarity import types


class ReagentLot(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/reagentlot}reagent-lot"

    reagent_kit = subnode_link(ReagentKit, "reagent-kit", attributes=('uri',))

    name = subnode_property("name")
    lot_number = subnode_property("lot-number")
    created_date = subnode_property("created-date", types.DATE)
    last_modified_date = subnode_property("last-modified-date", types.DATE)
    expiry_date = subnode_property("expiry-date", types.DATE)
    storage_location = subnode_property("storage-location")
    notes = subnode_property("notes")
    status = subnode_property("status")
    usage_count = subnode_property("usage-count", types.NUMERIC)
