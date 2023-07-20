try:
    from collections.abc import MutableSet
except ImportError:
    from collections import MutableSet
from s4.clarity import ETree, types
from s4.clarity._internal import WrappedXml
from s4.clarity._internal.props import attribute_property, subnode_property, subnode_link, subnode_links, subnode_element, subnode_property_literal_dict, subnode_property_dict, subnode_element_list
from utils.generic_testcases import LimsTestCase


class MockWrappedXml(WrappedXml):
    """
    Class to host test properties
    """

    # Attribute Properties
    root_attribute = attribute_property("root-attr")
    root_attribute_as_number = attribute_property("root-attr", types.NUMERIC)
    missing_attribute = attribute_property("missing-attribute")

    # Subnode Properties
    subnode = subnode_property("sub_node")
    missing_subnode = subnode_property("missing-subnode")

    # Subnode Link Properties
    subnode_link_read_only = subnode_link(WrappedXml, "link_node", readonly=True)
    subnode_link = subnode_link(WrappedXml, "link_node")

    subnode_links = subnode_links(WrappedXml, "link_node")

    # Subnode Proptery Literal Dictionary
    # # prop_name, subprop_name, name_attribute='name', value_attribute='value', readonly=False):
    subnode_property_literal_dict_instance = subnode_property_literal_dict("dict", "dict_entry")
    subnode_property_literal_dict__alt_names_instance = subnode_property_literal_dict("dict", "dict_entry", name_attribute="alt_name", value_attribute="alt_val")

    subnode_property_dict_instance = subnode_property_dict("dict", as_attributes=("name", "value"))


class SubNode(WrappedXml):
    node_one = subnode_property("node_one")
    node_two = subnode_property("node_two")


class RootElementWrapper(WrappedXml):
    sub_element = subnode_element(SubNode, "sub_node")
    sub_element_list = subnode_element_list(SubNode, "sub_nodes", "sub_node")

class PropertysTestCase(LimsTestCase):

    def test_attribute_property(self):
        xml = """
        <root_node root-attr='1' />
        """

        wrapped_xml = self.element_from_xml(MockWrappedXml, xml)

        # Verify that we can read the initial attribute value correctly
        assert(wrapped_xml.root_attribute == '1')

        # Verify that we can also read it as a Number
        assert(wrapped_xml.root_attribute_as_number == 1)

        # Set it with a new value as string
        wrapped_xml.root_attribute = '2'

        # Verify that the string can be read back and is the same
        assert(wrapped_xml.root_attribute == '2')

        # Verify that we can also read the change as a Number
        assert (wrapped_xml.root_attribute_as_number == 2)

        # Check if a missing attribute correctly reads as none
        assert(wrapped_xml.missing_attribute is None)

        # Create a new attribute to save the value
        wrapped_xml.missing_attribute = 'Sven'

        # Check if a missing attribute correctly reads as none
        assert (wrapped_xml.missing_attribute == 'Sven')

        # Check we can pass it None to delete the attribute
        wrapped_xml.missing_attribute = None

        # Verify the attribute has been removed
        assert (wrapped_xml.missing_attribute is None)

    def test_subnode_property(self):
        xml = """
        <root_node>
            <sub_node>Sub Node Value</sub_node>
        </root_node>"""

        wrapped_xml = self.element_from_xml(MockWrappedXml, xml)

        # Check initial value is being read
        assert(wrapped_xml.subnode == "Sub Node Value")

        # setting a new value
        wrapped_xml.subnode = "New value"

        # Verify that value was saved
        assert(wrapped_xml.subnode == "New value")

        # Read from a missing sub node
        assert(wrapped_xml.missing_subnode is None)

        # Create new subnode with value
        wrapped_xml.missing_subnode = "Missing Subnode Value"

        # Read from a missing sub node
        assert(wrapped_xml.missing_subnode == "Missing Subnode Value")

        # Delete the subnode
        wrapped_xml.missing_subnode = None

        # Verify it is missing
        assert(wrapped_xml.missing_subnode is None)

    def test_subnode_link(self):

        xml = """
        <root_node>
            <link_node limsid='1234' uri='http://qalocal/node/1234/' />
        </root_node>"""

        wrapped_xml = self.element_from_xml(MockWrappedXml, xml)

        # Verify that we got a FakeElement with the correct values pulled from the xml
        self.assertEqual(wrapped_xml.subnode_link.limsid, "1234")
        self.assertEqual(wrapped_xml.subnode_link.uri, "http://qalocal/node/1234/")

        tmp_xml = """
        <root_node>
            <link_node limsid='5678' uri='http://qalocal/node/5678/' />
        </root_node>"""

        tmp_element = self.element_from_xml(MockWrappedXml, tmp_xml)
        wrapped_xml.subnode_link = tmp_element.subnode_link

        # Modify the link
        self.assertEqual(wrapped_xml.subnode_link.limsid, "5678")

        # Verify the read only node can not be set
        def set_readonly_node():
            wrapped_xml.subnode_link_read_only = tmp_element.subnode_link
        self.assertRaises(AttributeError, set_readonly_node)

    def test_add_subnode_link(self):
        xml = """
            <root_node>
            </root_node>"""

        tmp_xml = """
        <root_node>
            <link_node limsid='1234' uri='http://qalocal/node/1234/' />
        </root_node>"""

        wrapped_xml = self.element_from_xml(MockWrappedXml, xml)

        tmp_element = self.element_from_xml(MockWrappedXml, tmp_xml)
        wrapped_xml.subnode_link = tmp_element.subnode_link

        # Verify that we got a FakeElement with the correct values pulled from the xml
        self.assertEqual(wrapped_xml.subnode_link.limsid, "1234")
        self.assertEqual(wrapped_xml.subnode_link.uri, "http://qalocal/node/1234/")

        # Modify the link
        wrapped_xml.subnode_link.limsid = "5678"
        self.assertEqual(wrapped_xml.subnode_link.limsid, "5678")

    def test_subnode_links(self):

        xml = """
        <root_element>
            <link_node limsid='1234' uri='https://qalocal/api/v2/samples/1234' />
            <link_node limsid='1235' uri='https://qalocal/api/v2/samples/1235' />
            <link_node limsid='1236' uri='https://qalocal/api/v2/samples/1236' />
        </root_element>"""

        wrapped_xml = self.element_from_xml(MockWrappedXml, xml)

        self.assertEqual(len(wrapped_xml.subnode_links), 3)
        self.assertEqual(wrapped_xml.subnode_links[0].limsid, "1234")
        self.assertEqual(wrapped_xml.subnode_links[1].limsid, "1235")
        self.assertEqual(wrapped_xml.subnode_links[2].limsid, "1236")

        def assign_node():
            wrapped_xml.subnode_links = wrapped_xml

        # Nodes are read only, we should not be able to assign to it
        self.assertRaises(AttributeError, assign_node)

    def test_subnode_element(self):
        xml = """
        <root_element>
            <sub_node>
                <node_one>value 1</node_one>
                <node_two>value 2</node_two>
            </sub_node>
        </root_element>
        """

        root_element = self.element_from_xml(RootElementWrapper, xml)

        self.assertTrue(isinstance(root_element.sub_element, SubNode))
        self.assertEqual(root_element.sub_element.node_one, "value 1")

    def test_subnode_element_list_remove(self):
        xml = """
            <root_element>
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
            </root_element>
            """

        root_element = self.element_from_xml(RootElementWrapper, xml)
        del root_element.sub_element_list[1]

        expected_xml_after_delete = """
            <root_element>
                <sub_nodes>
                    <sub_node>
                        <node_one>value 1</node_one>
                        <node_two>value 2</node_two>
                    </sub_node>
                    <sub_node>
                        <node_one>value 5</node_one>
                        <node_two>value 6</node_two>
                    </sub_node>
                </sub_nodes>
            </root_element>
            """

        self.assertXmlEqual(expected_xml_after_delete, root_element.xml)

    BASE_SUBNODE_ELEMENT_LIST_XML = """
        <root_element>
            <sub_nodes>
                <sub_node>
                    <node_one>value 1</node_one>
                    <node_two>value 2</node_two>
                </sub_node>
                <sub_node>
                    <node_one>value 3</node_one>
                    <node_two>value 4</node_two>
                </sub_node>
            </sub_nodes>
        </root_element>
        """

    def test_subnode_element_init(self):

        root_element = self.element_from_xml(RootElementWrapper, self.BASE_SUBNODE_ELEMENT_LIST_XML)

        # Verify some basic assumptaions about what we read
        self.assertTrue(isinstance(root_element.sub_element_list[0], SubNode))
        self.assertEqual(len(root_element.sub_element_list), 2)
        self.assertEqual(list(root_element.sub_element_list)[0].node_one, "value 1")

    def test_subnode_element_list_add(self):

        def add_and_check(inital_xml, after_xml, index):
            sub_node_xml = """
            <sub_node>
                <node_one>value 5</node_one>
                <node_two>value 6</node_two>
            </sub_node>
            """
            root_element = self.element_from_xml(RootElementWrapper, inital_xml)
            new_sub_node = self.element_from_xml(SubNode, sub_node_xml)
            root_element.sub_element_list.insert(index, new_sub_node)
            self.assertXmlEqual(after_xml, root_element.xml)

        # Complete with janky formatting that we get out of ETree after the insert
        expected_xml_add_index_0 = """
        <root_element>
            <sub_nodes>
                <sub_node>
                <node_one>value 5</node_one>
                <node_two>value 6</node_two>
            </sub_node><sub_node>
                    <node_one>value 1</node_one>
                    <node_two>value 2</node_two>
                </sub_node>
                <sub_node>
                    <node_one>value 3</node_one>
                    <node_two>value 4</node_two>
                </sub_node>
            </sub_nodes>
        </root_element>"""

        expected_xml_add_index_1 = """
            <root_element>
            <sub_nodes>
                <sub_node>
                    <node_one>value 1</node_one>
                    <node_two>value 2</node_two>
                </sub_node>
                <sub_node>
                <node_one>value 5</node_one>
                <node_two>value 6</node_two>
            </sub_node><sub_node>
                    <node_one>value 3</node_one>
                    <node_two>value 4</node_two>
                </sub_node>
            </sub_nodes>
        </root_element>"""

        expected_xml_add_index_2 = """
        <root_element>
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
            </sub_node></sub_nodes>
        </root_element>"""

        # Check that we can add to the start, middle and end
        add_and_check(self.BASE_SUBNODE_ELEMENT_LIST_XML, expected_xml_add_index_0, 0)
        add_and_check(self.BASE_SUBNODE_ELEMENT_LIST_XML, expected_xml_add_index_1, 1)
        add_and_check(self.BASE_SUBNODE_ELEMENT_LIST_XML, expected_xml_add_index_2, 2)

    def test_subnode_element_list_set(self):
        xml = """
            <root_element>
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
            </root_element>
            """

        new_node_xml = """
            <sub_node>
                <node_one>value 7</node_one>
                <node_two>value 8</node_two>
            </sub_node>"""

        root_element = self.element_from_xml(RootElementWrapper, xml)

        new_sub_element = self.element_from_xml(SubNode, new_node_xml)

        root_element.sub_element_list[0] = new_sub_element

        # More jankey white space
        expected_xml = """
            <root_element>
                <sub_nodes>
                    <sub_node>
                <node_one>value 7</node_one>
                <node_two>value 8</node_two>
            </sub_node><sub_node>
                        <node_one>value 3</node_one>
                        <node_two>value 4</node_two>
                    </sub_node>
                    <sub_node>
                        <node_one>value 5</node_one>
                        <node_two>value 6</node_two>
                    </sub_node>
                </sub_nodes>
            </root_element>
            """
        self.assertXmlEqual(expected_xml, root_element.xml)

    def test_subnode_property_literal_dict_init(self):
        xml = """
        <root_element>
            <dict>
                <dict_entry name='A' value='1' />
                <dict_entry name='B' value='2' />
                <dict_entry name='C' value='3' />
                <dict_entry name='D' value='4' />
            </dict>
        </root_element>"""

        wrapped_xml = self.element_from_xml(MockWrappedXml, xml)

        self.assertEqual(len(wrapped_xml.subnode_property_literal_dict_instance), 4)

        self.assertEqual(wrapped_xml.subnode_property_literal_dict_instance["A"], "1")
        self.assertEqual(wrapped_xml.subnode_property_literal_dict_instance["D"], "4")

    def test_subnode_property_literal_dict_modify_existing(self):
        xml = """
        <root_element>
            <dict>
                <dict_entry name='A' value='1' />
                <dict_entry name='B' value='2' />
                <dict_entry name='C' value='3' />
                <dict_entry name='D' value='4' />
            </dict>
        </root_element>"""

        wrapped_xml = self.element_from_xml(MockWrappedXml, xml)

        wrapped_xml.subnode_property_literal_dict_instance["A"] = "5"
        self.assertEqual(wrapped_xml.subnode_property_literal_dict_instance["A"], "5")

        # with jankey white space
        modified_xml = """
        <root_element>
            <dict>
                <dict_entry name='A' value='5' />
                <dict_entry name='B' value='2' />
                <dict_entry name='C' value='3' />
                <dict_entry name='D' value='4' />
            </dict>
        </root_element>"""

        self.assertXmlEqual(wrapped_xml.xml, modified_xml)


    def test_subnode_property_literal_dict_add(self):
        xml = """
        <root_element>
            <dict>
                <dict_entry name='A' value='1' />
                <dict_entry name='B' value='2' />
                <dict_entry name='C' value='3' />
                <dict_entry name='D' value='4' />
            </dict>
        </root_element>"""

        wrapped_xml = self.element_from_xml(MockWrappedXml, xml)

        wrapped_xml.subnode_property_literal_dict_instance["E"] = "77"

        # with jankey white space
        modified_xml = """
        <root_element>
            <dict>
                <dict_entry name='A' value='1' />
                <dict_entry name='B' value='2' />
                <dict_entry name='C' value='3' />
                <dict_entry name='D' value='4' />
            <dict_entry name="E" value="77" /></dict>
        </root_element>"""

        self.assertXmlEqual(wrapped_xml.xml, modified_xml)


    def test_subnode_property_literal_dict_itter(self):
        xml = """
        <root_element>
            <dict>
                <dict_entry name='A' value='1' />
                <dict_entry name='B' value='2' />
                <dict_entry name='C' value='3' />
                <dict_entry name='D' value='4' />
            </dict>
        </root_element>"""

        wrapped_xml = self.element_from_xml(MockWrappedXml, xml)

        expected_keys = ["A", "B", "C", "D"]
        for key, expected_key in zip(wrapped_xml.subnode_property_literal_dict_instance, expected_keys):
            self.assertEqual(key, expected_key)



    def test_subnode_property_literal_alternate_key_values(self):
        xml = """
        <root_element>
            <dict>
                <dict_entry name='A' value='1' alt_name="Z" alt_val="a" />
                <dict_entry name='B' value='2' alt_name="Y" alt_val="b" />
                <dict_entry name='C' value='3' alt_name="X" alt_val="c" />
                <dict_entry name='D' value='4' alt_name="W" alt_val="d" />
            </dict>
        </root_element>"""


        wrapped_xml = self.element_from_xml(MockWrappedXml, xml)

        dict = wrapped_xml.subnode_property_literal_dict__alt_names_instance
        self.assertEqual(len(dict), 4)
        self.assertEqual(dict["Z"], "a")
        self.assertEqual(dict["W"], "d")

        # Set a new value
        dict["R"] = "s"
        self.assertEqual(dict["R"], "s")

        # with jankey white space
        modified_xml = """
        <root_element>
            <dict>
                <dict_entry name='A' value='1' alt_name="Z" alt_val="a" />
                <dict_entry name='B' value='2' alt_name="Y" alt_val="b" />
                <dict_entry name='C' value='3' alt_name="X" alt_val="c" />
                <dict_entry name='D' value='4' alt_name="W" alt_val="d" />
            <dict_entry alt_name="R" alt_val="s"></dict_entry></dict>
        </root_element>"""

        self.assertXmlEqual(wrapped_xml.xml, modified_xml)


    def assertXmlEqual(self, xml_string_one, xml_string_two):
        self.assertEqual(self._normalize_xml(xml_string_one), self._normalize_xml(xml_string_two))

    @staticmethod
    def _normalize_xml(xml_string):
        xml_obj_one = ETree.fromstring(xml_string)
        return ETree.tostring(xml_obj_one)


    def test_subnode_property_dict(self):
        xml = """
            <root_element>
                <dict>
                    <dict_entry name='A' value='1' />
                    <dict_entry name='B' value='2' />
                    <dict_entry name='C' value='3' />
                    <dict_entry name='D' value='4' />
                </dict>
            </root_element>"""

        wrapped_xml = self.element_from_xml(MockWrappedXml, xml)
        dict = wrapped_xml.subnode_property_dict_instance
        pass

    def test_wrapped_xml_list(self):
        mutable_set = mutable_wrapped_xml_set()
        mutable_set.add(1)
        mutable_set.add(2)
        mutable_set.add(3)

        self.assertEqual(mutable_set, {1, 2, 3})

        mutable_set.discard(3)

        self.assertEqual(len(mutable_set), 2)
        self.assertEqual(mutable_set, {1, 2})

        #self.assertEqual(mutable_set[0], 1)


class mutable_wrapped_xml_set(MutableSet):
    _internal_set = set()

    def __init__(self):
        pass

    def __contains__(self, x):
        return self._internal_set.__contains__(x)

    def __iter__(self):
        return self._internal_set.__iter__()

    def discard(self, value):
        return self._internal_set.discard(value)

    def add(self, value):
        return self._internal_set.add(value)

    def __len__(self):
        return self._internal_set.__len__()

