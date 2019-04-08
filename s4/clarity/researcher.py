# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import FieldsMixin, ClarityElement
from s4.clarity.role import Role
from ._internal.props import subnode_property, subnode_links, subnode_link
from s4.clarity import ETree
from s4.clarity.lab import Lab


class Researcher(FieldsMixin, ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/researcher}researcher"
    ATTACH_TO_NAME = "ClientResearcher"

    first_name = subnode_property("first-name")
    last_name = subnode_property("last-name")
    email = subnode_property("email")
    initials = subnode_property("initials")

    lab = subnode_link(Lab, "lab", attributes=('uri',))

    username = subnode_property("credentials/username")
    password = subnode_property("credentials/password")
    roles = subnode_links(Role, "credentials/role")

    def add_role(self, new_role):
        credentials_node = self.xml_find('credentials')

        for child in credentials_node:
            if child.tag == "role" and child.get("name") == new_role.name:
                return

        ETree.SubElement(credentials_node, 'role', {"uri": new_role.uri})

    def remove_role(self, role):
        credentials_node = self.xml_find('credentials')

        nodes_to_remove = []

        for child in credentials_node:
            if child.tag == "role" and child.get("name") == role.name:
                nodes_to_remove.append(child)

        for n in nodes_to_remove:
            credentials_node.remove(n)
