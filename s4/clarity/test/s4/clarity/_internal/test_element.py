from s4.clarity._internal import WrappedXml
from s4.clarity.test.generic_testcases import LimsTestCase


class TestElement(LimsTestCase):

    def test_create_sub_node(self):
        samples = self.element_from_xml(WrappedXml, EMPTY_ELEMENT_XML)
        samples.set_subnode_text(INNER_NODE_NAME, "first value")
        self.assertEqual(samples.xml.decode(), ONE_INNER_NODE_XML)

    def test_modify_sub_node(self):
        samples = self.element_from_xml(WrappedXml, ONE_INNER_NODE_XML)
        samples.set_subnode_text(INNER_NODE_NAME, "second value")
        self.assertEqual(samples.xml.decode(), SECOND_INNER_NODE_XML)

    def test_empty_sub_node(self):
        samples = self.element_from_xml(WrappedXml, ONE_INNER_NODE_XML)
        samples.set_subnode_text(INNER_NODE_NAME, None)
        self.assertEqual(samples.xml.decode(), EMPTY_INNER_NODE)

INNER_NODE_NAME = "inner_node"
EMPTY_ELEMENT_XML = """<empty_element></empty_element>"""
ONE_INNER_NODE_XML = """<empty_element><inner_node>first value</inner_node></empty_element>"""
SECOND_INNER_NODE_XML = """<empty_element><inner_node>second value</inner_node></empty_element>"""
EMPTY_INNER_NODE = "<empty_element><inner_node /></empty_element>"