# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import collections
from six import string_types
from . import ClarityElement
from s4.clarity import ETree, types
from .lazy_property import lazy_property
from s4.clarity.types import obj_to_clarity_string, clarity_string_to_obj
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

FIELD_TAG = "{http://genologics.com/ri/userdefined}field"


class FieldsMixin(ClarityElement):

    # most elements put fields in '.', some are in './fields'.
    # must start with "./", or be a single period.
    FIELDS_XPATH = "."
    ATTACH_TO_NAME = None

    @lazy_property
    def fields(self):
        """:type: dict[str, object]"""
        if self.FIELDS_XPATH == ".":
            fields_node = self.xml_root
        else:
            fields_node = self.xml_find(self.FIELDS_XPATH)

            if fields_node is None:
                fields_node = self.make_subelement_with_parents(self.FIELDS_XPATH)

        return FieldsDict(fields_node)

    def get(self, name, default=None):
        """
        Get a UDF, if it exists.
        (Non-exception version of []).

        :type name: str
        :param default: returned if the item is not present
        :rtype: str or int or bool or datetime.datetime or float
        """
        if not isinstance(name, string_types):
            raise Exception("Non-string UDF names are invalid for Clarity elements.")

        return self.fields.get(name, default)

    def get_raw(self, name, default=None):
        """
        Get a UDF as a string, if it exists.

        :type name: str
        :param default: returned if the item is not present
        :rtype: str
        """
        if not isinstance(name, string_types):
            raise Exception("Non-string UDF names are invalid for Clarity elements.")

        return self.fields.get_raw(name, default)

    def get_formatted_number_string(self, name, default=None):
        """
        Get a Numeric UDF formatted to the correct precision, if the UDF exists.

        :type name: str
        :type default: str
        :param default: returned if the item is not present
        :rtype: str
        """
        if not isinstance(name, string_types):
            raise Exception("Non-string UDF names are invalid for Clarity elements.")

        raw_value = self.fields.get(name)

        if raw_value is None: # Compare against None, so as not to lose values of 0
            return default

        udf = self.get_udf_config(name)

        if udf.field_type != types.NUMERIC:
            raise Exception("'%s' can not be used with get_with_precision, as it is non-numeric." % name)

        # udf.precision will be None if 0 after Clarity 4.2.17
        return '{0:.{prec}f}'.format(raw_value, prec=int(udf.precision or 0))

    def get_udf_config(self, name):
        """
        Get the underlying UDF configuration associated with the field
        :param name: name of the field
        :rtype: s4.clarity.configuration.Udf
        """
        return self.lims.udfs.get_by_name(name, self._get_attach_to_key())

    def _get_attach_to_key(self):
        """
        Get the attach-to-name and attach-to-category properties for fetching the field's matching UDF object.
        Default implementation depends on the ATTACH_TO_NAME property being defined, and returns an empty category
        :rtype: str,str
        :return: a tuple of the attach-to-name and attach-to-category properties associated with the element type's UDFs
        """
        if not self.ATTACH_TO_NAME:
            raise Exception("Classes using the FieldsMixin must either provide a ATTACH_TO_NAME value, or override the "
                            "get_element_attach_to_values method.")

        return self.ATTACH_TO_NAME, ""

    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except KeyError:
            return False

    # delegate to fields
    def __getitem__(self, item):
        if not isinstance(item, string_types):
            raise Exception("Non-string UDF names are invalid for Clarity elements.", type(item))

        try:
            return self.fields.__getitem__(item)
        except KeyError:
            raise KeyError("No UDF '%s' defined on %s." % (item, self))

    # delegate to fields
    def __setitem__(self, key, value):
        if not isinstance(key, string_types):
            raise Exception("Non-string UDF names are invalid for Clarity elements.")

        return self.fields.__setitem__(key, value)

    def __delitem__(self, key):
        if not isinstance(key, string_types):
            raise Exception("Non-string UDF names are invalid for Clarity elements.")

        return self.fields.__delitem__(key)

    def __iter__(self):
        return self.fields.__iter__()

    @property
    def xml_root(self):
        return super(FieldsMixin, self).xml_root

    @xml_root.setter
    def xml_root(self, root_node):
        """
        NOTE: setting xml_root directly will end-run around dirty object tracking.
        """
        super(FieldsMixin,type(self)).xml_root.__set__(self, root_node)

        if root_node is not None:
            # wipe our fields cache
            self.__dict__.pop('fields', None)

            # comma decimal mark workaround
            # This works around the Clarity issue with non-english locales, where numeric values from Clarity
            # are output by Clarity with commas as the decimal mark, but Clarity cannot accept them as input.
            for subnode in root_node.findall(self.FIELDS_XPATH + '/' + FIELD_TAG):
                if subnode.get('type') == types.NUMERIC:
                    subnode.text = subnode.text.replace(',', '.')


class FieldsDict(MutableMapping):
    """
    :type _real_dict: dict[str, ETree.Element]
    :type _root_node: ETree.Element
    """

    def __init__(self, fields_node):
        """
        :type fields_node: ETree.Element
        """

        d = {}
        for subnode in fields_node.findall('./' + FIELD_TAG):
            d[subnode.get("name")] = subnode

        self._real_dict = d
        self._value_cache = {}
        self._root_node = fields_node

    def __len__(self):
        return len(self._real_dict)

    def __setitem__(self, key, value):
        """
        NOTE: The value should already be the correct type.

        :type key: str
        :type value: object
        """
        field_node = self._get_or_create_node(key)
        field_node.text = obj_to_clarity_string(value)

        self._value_cache[field_node] = value

    def _get_or_create_node(self, key):
        """
        Get a field XML node, or create and append it to the XML fields node if it doesn't exist.

        :type key: str
        :rtype: ETree.Element
        """
        field_node = self._real_dict.get(key)
        if field_node is None:
            field_node = ETree.SubElement(self._root_node, FIELD_TAG)
            field_node.set('name', key)
            self._real_dict[key] = field_node
        return field_node

    def __getitem__(self, key):
        """
        Returns a field (UDF) value.
        The return type can be any of bool, str, float, datetime.

        :rtype: object
        :type key: str
        """
        field_node = self._real_dict[key]
        return self._node_python_value(field_node)

    def get_raw(self, key, default=None):
        """
        Returns an untranslated string value of a UDF.
        :type key: str
        :type default: str or None
        :rtype: str or None
        """

        field_node = self._real_dict[key]
        return field_node.text if field_node is not None else default

    def _node_python_value(self, field_node):
        if field_node in self._value_cache:
            return self._value_cache[field_node]

        else:
            field_type = field_node.get('type')
            value = clarity_string_to_obj(field_type, field_node.text)
            self._value_cache[field_node] = value
            return value

    def get_type(self, key):
        """
        Returns the type of a Clarity field.

        :type key: str
        :returns: any of FieldsDict.TYPES
        :rtype: str
        """
        field_node = self._real_dict[key]
        if field_node is None:
            return None
        else:
            return field_node.get('type')

    def __delitem__(self, key):
        """
        Delete an item in the field dictionary by setting it to None, which will send the empty string
        as a value to Clarity.
        """
        self.__setitem__(key, None)

    def __iter__(self):
        """Return an iterator over field names."""
        return self._real_dict.__iter__()

    def itervalues(self):
        """Return an iterator over deserialized field values."""
        for key in self._real_dict:
            node = self._real_dict[key]
            yield self._node_python_value(node)

    def iteritems(self):
        """Return an iterator over (field name, field value (deserialized)) pairs."""
        for key in self._real_dict:
            node = self._real_dict[key]
            value = self._node_python_value(node)
            yield (key, value)

    def __contains__(self, x):
        return self._real_dict.__contains__(x)
