# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from s4.clarity._internal import ClarityElement, lazy_property
from s4.clarity._internal.props import subnode_property
from s4.clarity import types


class ReagentKit(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/reagentkit}reagent-kit"

    name = subnode_property("name")
    supplier = subnode_property("supplier")
    catalogue_number = subnode_property("catalogue-number")
    website = subnode_property("website", types.URI)
    archived = subnode_property("archived", types.BOOLEAN)

    @lazy_property
    def related_reagent_lots(self):
        return self.lims.reagent_lots.query(kitname=self.name)
