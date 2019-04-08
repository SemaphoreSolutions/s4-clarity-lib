# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
from s4.clarity import ETree
from s4.clarity._internal import ClarityElement
from s4.clarity._internal.props import subnode_property, attribute_property
from s4.clarity import types


class Udf(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/configuration}udfconfig"
    CREATION_TAG = "{http://genologics.com/ri/configuration}field"

    # Alternate name to avoid collision with built-in 'type'
    field_type = attribute_property("type") # type: str
    attach_to_name = subnode_property("attach-to-name") # type: str
    show_in_lablink = subnode_property("show-in-lablink", types.BOOLEAN) # type: bool
    allow_non_preset_values = subnode_property("allow-non-preset-values", types.BOOLEAN) # type: bool
    first_preset_is_default_value = subnode_property("first-preset-is-default-value", types.BOOLEAN) # type: bool
    show_in_tables = subnode_property("show-in-tables", types.BOOLEAN) # type: bool
    is_editable = subnode_property("is-editable", types.BOOLEAN) # type: bool
    is_deviation = subnode_property("is-deviation", types.BOOLEAN) # type: bool
    is_controlled_vocabulary = subnode_property("is-controlled-vocabulary", types.BOOLEAN) # type: bool
    is_required = subnode_property("is-required", types.BOOLEAN) # type: bool
    attach_to_category = subnode_property("attach-to-category") # type: str

    # Only valid for Numeric types
    min_value = subnode_property("min-value", types.NUMERIC)  # type: float
    max_value = subnode_property("max-value", types.NUMERIC)  # type: float
    precision = subnode_property("precision", types.NUMERIC)  # type: float

    @property
    def presets(self):
        """
        :type: list
        """
        preset_nodes = self.xml_root.findall('preset')
        return [types.clarity_string_to_obj(self.field_type, preset_node.text) for preset_node in preset_nodes]

    def add_preset(self, new_preset_value):
        """
        Add a new preset value to the end of the list. Ignores values that are already present.

        :type new_preset_value: str|unicode|int|float|datetime.date|bool
        :param new_preset_value: the preset value to add, with a type appropriate to the UDF. The value is not
            validated to be the correct type.
        """
        preset = self._find_preset_by_value(new_preset_value)

        if preset is not None:
            return

        self._add_preset_internal(new_preset_value)

    def remove_preset(self, preset_value):
        """
        Remove a preset value from the list.

        :type preset_value: str|unicode|int|float|datetime.date|bool
        :param preset_value: the preset value to remove, with a type appropriate to the UDF. The value is
            not validated to be the correct type.
        """
        preset = self._find_preset_by_value(preset_value)

        if preset is not None:
            self.xml_root.remove(preset)

    def set_default_preset(self, default_preset_value):
        """
        Sets a preset value as the default (puts first in the list). Adds value if it isn't already preset.

        :type default_preset_value: str|unicode|int|float|datetime.date|bool
        :param default_preset_value: the new default preset value, with a type appropriate to the UDF. The value is
            not validated to be the correct type.
        :raises Exception: if the udf's first-preset-is-default property is currently false
        """
        if not self.first_preset_is_default_value:
            raise Exception("Setting the default value will have no effect, as first-preset-is-default-value is false.")

        current_preset_nodes = self.xml_findall('preset')

        # Initialize the new list of presets with the default
        new_preset_values = [types.obj_to_clarity_string(default_preset_value)]

        for preset in current_preset_nodes:
            # Only grab values other than the new default, in case it was already in there
            if types.clarity_string_to_obj(self.field_type, preset.text) != default_preset_value:
                new_preset_values.append(preset.text)

            self.xml_root.remove(preset)

        for preset_value in new_preset_values:
            self._add_preset_internal(preset_value)

    def _find_preset_by_value(self, preset_value):
        all_presets = self.xml_root.findall("preset")

        for preset in all_presets:
            if types.clarity_string_to_obj(self.field_type, preset.text) == preset_value:
                return preset

    def _add_preset_internal(self, preset_value):
        preset_node = ETree.SubElement(self.xml_root, 'preset')
        preset_node.text = types.obj_to_clarity_string(preset_value)

