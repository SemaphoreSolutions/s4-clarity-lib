# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from s4.clarity import ETree
import logging
import inspect
from six import string_types
from abc import ABCMeta, abstractmethod
try:
    from collections.abc import MutableSequence, MutableMapping
except ImportError:
    from collections import MutableSequence, MutableMapping

from s4.clarity import types

log = logging.getLogger(__name__)


class _clarity_property(object):
    """
    Abstract class to hold code common to each type of property.

    Inheritors must call _ensure_settable in __set__.
    """
    __metaclass__ = ABCMeta

    def __init__(self, property_name, readonly=False, property_type_str=None):
        """
        :type property_name: str
        :type readonly: bool
        """

        self.property_name = property_name
        self.readonly = readonly

        self.__doc__ = "The value of the XML property '%s'" % property_name

        if property_type_str:
            self.__doc__ += "\n\n:type: %s" % property_type_str

        self.__name__ = property_name
        self.__module__ = _prop_defining_module()

    @abstractmethod
    def __get__(self, instance, owner):
        """
        Returns the value of this property.
        :param instance: Instance is the instance that the attribute was accessed through that provides the backing xml data.
        :param owner: The class of the owning object.
        """
        return None

    def __set__(self, instance, value):
        """
        :param instance: Instance is the instance that the attribute was accessed through that provides the backing xml data.
        :param value: The value to set.
        """
        # this does nothing, but in the case of an always-readonly class, we call this to
        # ensure we are properly raising an error.
        self._ensure_settable(instance)

    def _ensure_settable(self, instance):
        if self.readonly:
            raise AttributeError("%s.%s is a read-only property." % (instance, self.property_name))


class attribute_property(_clarity_property):
    """
    Creates a property that is backed against a xml attribute on the root element of a WrappedXml object.
    ex:
    <root_node demo_attribute='demo value' />

    class RootElementWrapper(WrappedXml):
        demo_attribute = attribute_property("demo_attribute")

    root.demo_attribute == 'demo_value'
    """
    def __init__(self, property_name, typename=types.STRING, readonly=False):
        """
        :type typename: str
        :param typename: one of s4.clarity.types, default STRING.
        """
        prop_typename = types.clarity_typename_to_python_typename(typename)
        super(attribute_property, self).__init__(property_name, readonly, prop_typename)
        self.typename = typename

    def __get__(self, instance, owner):
        """
        :type instance: s4.clarity._internal.element.WrappedXml
        """
        string_value = instance.xml_root.attrib.get(self.property_name)
        return types.clarity_string_to_obj(self.typename, string_value)

    def __set__(self, instance, value):
        """
        Setting the value to None will cause the attribute to be deleted.

        :param instance:
        :type instance: s4.clarity._internal.element.WrappedXml
        :param value:
        """

        self._ensure_settable(instance)

        if value is None:
            instance.xml_root.attrib.pop(self.property_name, None)
        else:
            string_value = types.obj_to_clarity_string(value)
            instance.xml_root.set(self.property_name, string_value)


class subnode_property(_clarity_property):
    """
    Creates a property with a simple value that is backed against a xml sub-element owned by the root node.
    ex:
    <root_element>
        <sub_element>Sub Element Value</sub_element>
    </root_element>

    class RootElementWrapper(WrappedXml):
        sub_element = subnode_property("sub_element")

    root.sub_element == 'Sub Element Value'
    """

    def __init__(self, property_name, typename=types.STRING, readonly=False):
        """
        :param property_name: The name of the xml element to use as a backing value.
        :type property_name: str

        :param typename: one of s4.clarity.types, default STRING
        :type typename: str

        :param readonly: When set to True an AttributeError will be thrown if this property is written to.
        :type readonly: bool
        """

        prop_typename = types.clarity_typename_to_python_typename(typename)
        super(subnode_property, self).__init__(property_name, readonly, prop_typename)
        self.typename = typename

    def __get__(self, instance, owner):
        """
        :param instance: The instance that the attribute was accessed through, or None when the attribute is accessed through the owner.
        :type instance: s4.clarity._internal.element.WrappedXml

        :param owner: The owner of the class
        :type owner: Type
        """
        string_value = instance.get_node_text(self.property_name)
        return types.clarity_string_to_obj(self.typename, string_value)

    def __set__(self, instance, value):
        """
        Setting the value to None will cause the subnode (self.prop_name) to be deleted.

        :type instance: s4.clarity._internal.element.WrappedXml
        :raises AttributeError: If this is a read-only property.
        """
        self._ensure_settable(instance)

        if value is None:
            instance.remove_subnode(self.property_name)
        else:
            string_value = types.obj_to_clarity_string(value)
            instance.set_subnode_text(self.property_name, string_value)


class subnode_link(_clarity_property):
    """
    Creates a property that is backed by a subnode link data structure, which is a
    node with the 'limsid' and 'uri' attributes. This property will return a ClarityElement
    for the data structure backed against the data from the uri.

    ex:
    <root_node>
        <sample_node limsid='1234' uri='https://qalocal/api/v2/samples/1234' />
    </root_node>

    class RootNodeWrapper(WrappedXml):
        sample = subnode_link(Sample, "sample_node")

    root.sample == <Sample limsid='1234'>
    """

    def __init__(self, element_type, property_name, readonly=False, attributes=('limsid', 'uri')):
        """
        :type element_type: Type[s4.clarity._internal.element.ClarityElement]
        :type property_name: str
        :type attributes: tuple[str]

        :param readonly: When set to True an AttributeError will be thrown if this property is written to.
        :type readonly: bool
        """
        super(subnode_link, self).__init__(property_name, readonly)
        self.element_type = element_type
        self.link_attributes = attributes

        self.__doc__ = """The linked `{0}` from the '{1}' subnode
        
                          :type: {0}""".format(element_type.__name__, property_name)

    def __get__(self, instance, owner):
        """
        :type instance: s4.clarity._internal.element.WrappedXml
        :rtype: s4.clarity._internal.element.ClarityElement
        """
        return instance.lims.factory_for(self.element_type).from_link_node(instance.xml_find("./" + self.property_name))

    def __set__(self, instance, value):
        """
        :type instance: s4.clarity._internal.element.WrappedXml
        :type value: s4.clarity._internal.element.ClarityElement
        """
        self._ensure_settable(instance)

        # a link is of the form:
        # <project limsid="SWI1" uri="https://qalocal/api/v2/projects/SWI1"/>

        node = instance.get_or_create_subnode(self.property_name)
        attribs = {}

        for attrname in self.link_attributes:
            if hasattr(value, attrname):
                attrvalue = getattr(value, attrname)

                if attrvalue is not None:
                    attribs[attrname] = attrvalue

        if node is None:
            ETree.SubElement(instance.xml_root, self.property_name, attribs)
        else:
            for k, v in attribs.items():
                node.set(k, v)


class subnode_links(_clarity_property):
    """
        Creates a property that backs against a number of elements with the subnode link data structure,
        which is a node with the 'limsid' and 'uri' attributes. This node will return a list of ClarityElements
        similar to the output of subnode_link.

       ex:
       <root_node>
           <link_node limsid='1234' uri='https://qalocal/api/v2/samples/1234' />
           <link_node limsid='1235' uri='https://qalocal/api/v2/samples/1235' />
           <link_node limsid='1236' uri='https://qalocal/api/v2/samples/1236' />
       </root_node>

       class RootElementWrapper(WrappedXml):
           sub_element = subnode_link(Sample, "link_node")

       root.sub_element == [<Sample limsid='1234'>, <Sample limsid='1235'>, <Sample limsid='1236'>]
       """

    def __init__(self, element_type, property_name, container_name=None):
        """
        :type element_type: Type[s4.clarity._internal.element.ClarityElement]
        :type property_name: str
        :type container_name: str
        """
        super(subnode_links, self).__init__(property_name, readonly=True)

        self.element_type = element_type
        if container_name is None:
            self.link_path = "./{0}".format(property_name)
        else:
            self.link_path = "./{0}/{1}".format(container_name, property_name)

        self.__doc__ = """The linked `{0}` objects from the '{1}' subnodes
        
                          :type: list[{0}]""".format(element_type.__name__, property_name)

    def __get__(self, instance, owner):
        """
        :type instance: s4.clarity._internal.element.WrappedXml
        :rtype: s4.clarity._internal.element.ClarityElement
        """
        return instance.lims.factory_for(self.element_type).from_link_nodes(instance.xml_findall(self.link_path))


class subnode_element(_clarity_property):
    """
        Creates a property that backs against a sub node which contains data structure that can be represented by
        a object derived from WrappedXml.

       ex:
        <root_node>
            <sub_node>
                <node_one>value 1</node_one>
                <node_two>value 2</node_two>
            </sub_node>
        </root_node>

        class SubNode(WrappedXml):
            node_one = subnode_property("node_one")
            node_two = subnode_property("node_two")

       class RootNodeWrapper(WrappedXml):
           sub_element = subnode_element(SubNode, "sub_node")

       root.sub_element.node_one == "value 1"
    """

    def __init__(self, element_class, property_name, readonly=False):
        """
        :type element_class: Type[s4.clarity._internal.element.WrappedXml]
        :type property_name: str

        :param readonly: When set to True an AttributeError will be thrown if this property is written to.
        :type readonly: bool
        """
        super(subnode_element, self).__init__(property_name, readonly)
        self.element_class = element_class

        self.__doc__ = """The element `{0}` from subnode '{1}'
        
                          :type: {0}""".format(element_class.__name__, property_name)

    def __get__(self, instance, owner):
        """
        :type instance: s4.clarity._internal.element.WrappedXml
        :rtype: s4.clarity._internal.element.WrappedXml
        """

        # ToDo: This sould be cached so that we return the same object each time otherwise root.sub_element != root.sub_element
        return self.element_class(instance.lims, instance.get_or_create_subnode(self.property_name))

    def __set__(self, instance, value):
        """
        :type instance: s4.clarity._internal.element.WrappedXml
        :type value: s4.clarity._internal.element.WrappedXml
        """
        self._ensure_settable(instance)

        node = instance.xml_find(self.property_name)

        if node:
            instance.xml_root.remove(node)

        instance.xml_root.append(value.xml_root)


class subnode_element_list(_clarity_property):
    """
        Creates a property that backs onto a list of subnodes which contains data structure that can be represented by
        a object derived from WrappedXml.

        ex:
        <root_node>
            <sub_nodes>
                <sub_node>
                    <node_one>value 1</node_one>
                    <node_two>value 2</node_two>
                </sub_node>
                <sub_node>
                    <node_one>value 3</node_one>
                    <node_two>value 4</node_two>
                </sub_node>
                <sub_node>
                    <node_one>value 5</node_one>
                    <node_two>value 6</node_two>
                </sub_node>
            </sub_nodes>
        </root_node>

        class SubNode(WrappedXml):
            node_one = subnode_property("node_one")
            node_two = subnode_property("node_two")

        class RootElementWrapper(WrappedXml):
            sub_element = subnode_element(SubNode, "sub_nodes", "sub_node")

        root.sub_element == [<SubNode>, <SubNode>, <SubNode>]
        root.sub_element[0].node_one == "value 1"
        root.sub_element[2].node_two == "value 6"
    """

    def __init__(self, element_class, property_name, list_item_property_name, readonly=False):
        """
        :param element_class: The class
        :type element_class: Type[s4.clarity._internal.element.WrappedXml]

        :param property_name: The name of the xml element that contains the sub items to be used as backing values for this list.
        :type property_name: str

        :param list_item_property_name: The name of the xml elements that will be used as backing values for indivdual items in this list.
        :type list_item_property_name: str

        :param readonly: When set to True an AttributeError will be thrown if this property is written to.
        :type readonly: bool
        """

        super(subnode_element_list, self).__init__(property_name, readonly)

        self.element_class = element_class
        self.list_item_property_name = list_item_property_name
        self.__doc__ = """`{0}` items from the '{1}' subnodes
        
            :type: list[{0}]""".format(element_class.__name__, list_item_property_name)

    def __get__(self, instance, owner):
        """
        :param instance: The owning object.
        :type instance: s4.clarity._internal.element.WrappedXml
        :rtype: list[s4.clarity._internal.element.WrappedXml]
        """
        return _ClarityWrappedXmlList(self.element_class, instance, self.property_name, self.list_item_property_name, self.readonly)

    def __set__(self, instance, value):
        """
        :type instance: s4.clarity._internal.element.WrappedXml
        :type value: list[s4.clarity._internal.element.WrappedXml]
        """
        self._ensure_settable(instance)

        nodes = instance.xml_findall(self.property_name)

        if nodes:
            [instance.xml_root.remove(node) for node in nodes]

        [instance.xml_root.append(item.xml_root) for item in value]


class _ClarityWrappedXmlList(MutableSequence):
    def __init__(self, element_class, node_instance, property_name, list_item_property_name, readonly=False):
        """
        Represents a list of sub nodes as an object list.
        :param element_class: The class used to represent nodes as objects.
        :type element_class: WrappedXml derived class

        :param node_instance: The owning WrappedXml object that contains the backing xml.
        :type node_instance: WrappedXml derived

        :param property_name: The name of the xml element that contains the list of nodes.
        :type property_name: str

        :param list_item_property_name: The name of the xml element that represents the nodes.
        :type list_item_property_name: str

        :param readonly: When set to True an AttributeError will be thrown if this property is written to.
        :type readonly: bool
        """
        self._element_class = element_class
        self._parent_element = node_instance
        self._property_name = property_name
        self._list_property_name = list_item_property_name
        self._read_only = readonly

        self._inner_list = self._get_list_nodes()

    def _get_list_nodes(self):

        root_element = self._get_list_root_element()
        if root_element is None:
            return []

        sub_nodes = root_element.findall(self._list_property_name)
        return [self._element_class(self._parent_element.lims, node) for node in sub_nodes]

    def _ensure_settable(self):
        if self._read_only:
            raise AttributeError("%s.%s is a read-only property." % (self._parent_element, self._list_property_name))

    def __len__(self):
        return len(self._inner_list)

    def __delitem__(self, index):

        # Verify we can modify this structure
        self._ensure_settable()

        # Remove the element from xml
        element = self._inner_list[index]
        root_element = self._get_list_root_element()
        if root_element is not None:
            root_element.remove(element.xml_root)

        # Remove the element from the in memory list
        del self._inner_list[index]

    def insert(self, index, value):
        # Verify we can modify this structure
        self._ensure_settable()

        # Add the item to be a child of the list root element
        root_element = self._get_or_create_list_root_element()
        root_element.insert(index, value.xml_root)

        # Insert into the in memory list
        self._inner_list.insert(index, value)

    def __setitem__(self, index, value):
        # Verify we can modify this structure
        self._ensure_settable()

        # Update the backing xml
        root_element = self._get_or_create_list_root_element()
        root_element[index] = value.xml_root

        # Modify the in memory list
        self._inner_list.__setitem__(index, value)

    def __getitem__(self, index):
        return self._inner_list.__getitem__(index)

    def _get_list_root_element(self):
        """
        Shortcut to the wrapper element for the list.
        :return: The Etree element that is described in the _property_name xpath, or None
        :rtype: ETree.Element
        """
        return self._parent_element.xml_find(self._property_name)

    def _get_or_create_list_root_element(self):
        """
        Shortcut to the wrapper element for the list. If the element does not exist it will
        be created
        :return: The Etree element that is described in the _property_name xpath.
        :rtype: ETree.Element
        """
        return self._parent_element.get_or_create_subnode(self._property_name)


class _ClarityLiteralDict(MutableMapping):
    """
    :type top_node: ETree.Element
    """

    def __init__(self, top_node, subnode_name, name_attribute, value_attribute):
        self.top_node = top_node
        self.subnode_name = subnode_name
        self.name_attribute = name_attribute
        self.value_attribute = value_attribute

    def __iter__(self):
        # Return an iterator of all keys, like a dict
        all_keys = map(self._get_node_key, self._get_all_nodes())
        return iter(all_keys)

    def __len__(self):
        return len(self._get_all_nodes())

    def __delitem__(self, key):
        node = self._node_for(key)
        if node is None:
            raise KeyError
        self.top_node.remove(node)

    def __setitem__(self, key, value):
        node = self._node_for(key)
        if node is None:
            node = ETree.SubElement(self.top_node, self.subnode_name, {self.name_attribute: key})
        node.set(self.value_attribute, value)

    def __getitem__(self, key):
        node = self._node_for(key)
        if node is None:
            raise KeyError
        return node.get(self.value_attribute)

    def _node_for(self, key):
        nodes = self._get_all_nodes()
        for n in nodes:
            if self._get_node_key(n) == key:
                return n
        return None

    def _get_node_key(self, node):
        return node.get(self.name_attribute)

    def _get_all_nodes(self):
        return self.top_node.findall('./' + self.subnode_name)


class subnode_property_literal_dict(subnode_property):
    """
    If there is a dictionary represented in xml with key/value subnodes this will turn it into a dictionary.
    """

    def __init__(self, prop_name, subprop_name, name_attribute='name', value_attribute='value', readonly=False):
        """

        :param prop_name:
        :param subprop_name:
        :param name_attribute:
        :param value_attribute:

        :param readonly: When set to True an AttributeError will be thrown if this property is written to.
        :type readonly: bool
        """

        super(subnode_property_literal_dict, self).__init__(prop_name, readonly=readonly)
        self.subprop_name = subprop_name
        self.name_attribute = name_attribute
        self.value_attribute = value_attribute
        self._dict = None

    def _get_or_make_dict(self, instance):

        node = instance.xml_find('./' + self.property_name)

        # we check node in case we've gotten a new xml tree and still have the old dict.
        if self._dict is not None and self._dict.top_node == node:
            return self._dict

        if node is None:
            node = ETree.SubElement(instance.xml_root, self.property_name)

        return _ClarityLiteralDict(node, self.subprop_name, self.name_attribute, self.value_attribute)

    def __get__(self, instance, owner):
        """
        :type instance: s4.clarity._internal.element.ClarityElement
        :rtype: dict
        """
        return self._get_or_make_dict(instance)

    def __set__(self, instance, new_dict):
        """
        :type instance: s4.clarity._internal.element.ClarityElement
        :type new_dict: dict
        """
        self._ensure_settable(instance)

        # this ought to work with .update,
        our_dict = self._get_or_make_dict(instance)
        our_dict.update(new_dict)


class subnode_property_dict(subnode_property):
    """
    Takes a subnode that contains a dictionary, searching by property name.
    The content of the element is turned into the dictionary.
    """

    def __init__(self, property_name, as_attributes=(), readonly=False):
        """

        :param property_name:
        :param as_attributes:

        :param readonly: When set to True an AttributeError will be thrown if this property is written to.
        :type readonly: bool
        """
        super(subnode_property_dict, self).__init__(property_name, readonly=readonly)



        self.as_attributes = as_attributes

    def __get__(self, instance, owner):
        """
        :type instance: s4.clarity._internal.element.ClarityElement
        :rtype: dict
        """
        node = instance.xml_find('./' + self.property_name)

        return self._node_into_dict(node)

    def _node_into_dict(self, node):
        if node.text is None or node.text.strip() == "":
            d = dict()
            for sub in node:
                key = sub.tag
                value = self._node_into_dict(sub)

                if key in d:
                    value_already = d[key]
                    if type(value_already) == list:
                        value_already.append(value)
                    else:
                        d[key] = [value_already, value]
                else:
                    d[key] = value

            for attrname in self.as_attributes:
                key = attrname
                value = node.get(key)
                if value is not None:
                    d[key] = value

            return d
        else:
            return node.text

    @staticmethod
    def _value_to_string(value):
        if value is None:
            raise Exception("Can't serialize None as XML value")
        elif type(value) in (string_types, int):
            # simple types which we know are ok
            return str(value)
        elif type(value) == bool:
            return "true" if value else "false"
        else:
            log.warning("stringifying value %r for XML: %s", value, str(value))
            return str(value)

    def _dict_into_node(self, instance, value, parent, name, node=None):
        if node is None:
            node = parent.find('./' + name) or ETree.SubElement(parent, name)

        if type(value) == dict:
            for k, v in value.items():
                if k in self.as_attributes:
                    node.set(k, self._value_to_string(v))
                else:
                    self._dict_into_node(instance, v, node, k)
        elif type(value) == list:
            for subvalue in value:
                # call self again, but value = subvalue, prechosen node
                self._dict_into_node(instance, subvalue, parent, name, node)
                # get a new node
                node = ETree.SubElement(parent, name)
            # release the last node in the list
            parent.remove(node)
        else:
            node.text = self._value_to_string(value)

    def __set__(self, instance, value):
        """
        :type instance: s4.clarity._internal.element.ClarityElement
        :type value: dict[str, any]
        """
        self._ensure_settable(instance)

        self._dict_into_node(instance, value, instance.xml_root, self.property_name)


class subnode_property_list_of_dicts(subnode_property_dict):
    def __init__(self, property_name, as_attributes=(), order_by=None):
        super(subnode_property_list_of_dicts, self).__init__(property_name, as_attributes)
        self.__doc__ = "Retrieves the value of the property '%s'\n\n:type: list[dict]" % property_name
        self.order_by = order_by

    def __get__(self, instance, owner):
        """
        :type instance: s4.clarity._internal.element.ClarityElement
        :rtype: list[dict]
        """
        nodes = instance.xml_findall('./' + self.property_name)
        the_list = [self._node_into_dict(node) for node in nodes]
        if self.order_by is None:
            return the_list
        else:
            return sorted(the_list, key=self.order_by)

    def __set__(self, instance, the_list):
        """
        :type instance: s4.clarity._internal.element.ClarityElement
        :type the_list: list[dict[str, any]]
        """
        self._ensure_settable(instance)

        if self.order_by is not None:
            last_key = None
            for item in the_list:
                this_key = self.order_by(item)
                if last_key is not None and this_key < last_key:
                    raise Exception("List given for %s should be ordered by %s, but value %r is out of order" %
                                    (self.property_name, self.order_by, this_key),
                                    item, last_key, this_key)
                last_key = this_key

        xpath = './' + self.property_name
        split_path = xpath.split("/")
        parent_path = "/".join(split_path[:-1]) + "/"
        parent = instance.xml_find(parent_path)
        node_name = split_path[-1]

        for matching_node in [n for n in list(parent) if n.tag.lower() == node_name.lower()]:
            parent.remove(matching_node)

        self._dict_into_node(instance, the_list, parent, node_name)


def _prop_defining_module():

    frame = inspect.currentframe()
    modulename = None

    while modulename is None or modulename == __name__:
        modulename = frame.f_locals.get('__module__')
        frame = frame.f_back
        if frame is None:
            break

    # frames are special and are not properly reference-counted, so must be deleted explicitly
    del frame
    return modulename
