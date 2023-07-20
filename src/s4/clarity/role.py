# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from s4.clarity._internal import ClarityElement, lazy_property
from s4.clarity._internal.props import subnode_links
from s4.clarity.permission import Permission


class Role(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/role}role"

    # Not using subnode_links for this property, as it requires a Researcher import that creates a circular dependency
    @lazy_property
    def researchers(self):
        """
        :type: list[Researcher]
        """
        return self.lims.researchers.from_link_nodes(self.xml_findall("researchers/researcher"))

    permissions = subnode_links(Permission, "permissions/permission")
