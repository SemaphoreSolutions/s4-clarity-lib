# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from future.utils import python_2_unicode_compatible
from ._internal import ClarityElement
from ._internal.props import subnode_property, subnode_property_literal_dict
from s4.clarity import ETree


class ReagentType(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/reagenttype}reagent-type"

    @python_2_unicode_compatible
    def __str__(self):
        return u"<%s %s>" % (self.__class__.__name__, self.name)

    reagent_category = subnode_property("reagent-category")
    attributes = subnode_property_literal_dict("special-type", "attribute")

    @property
    def name(self):
        if self._name is None:
            name = self.xml_root.get("name")
            self._name = name
        return self._name

    @name.setter
    def name(self, value):
        self.xml_root.set("name", value)
        self._name = value

    @property
    def special_type(self):
        # type: () -> str
        """
        :type: str
        """
        special_type = self.xml_find("./special-type")
        return special_type.get("name")

    @special_type.setter
    def special_type(self, value):
        special_type = self.xml_find("./special-type")
        if special_type is None:
            special_type = ETree.SubElement(self.xml_root, "special-type")
        special_type.set("name", value)
