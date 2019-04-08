# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import s4.clarity
from s4.clarity import ETree
from s4.clarity.artifact import Artifact
from s4.clarity.step import StepDetails
from s4.clarity.test.generic_testcases import LimsTestCase


class TestFields(LimsTestCase):

    lims = s4.clarity.LIMS(root_uri='https://www.example.com/', username='', password='')

    def _assert_xml_has_value(self, element, expected_value, msg=None,
                              xpath="{http://genologics.com/ri/userdefined}field"):
        udfnode = element.xml_root.find(xpath)
        msg = " %s" % msg if msg else ""
        self.assertTrue(udfnode is not None, "has a UDF node" + msg)
        self.assertEqual(udfnode.text, expected_value, ("has expected value %r in XML" % expected_value) + msg)

    def test_field_is_none(self):
        element = self.lims.artifacts.new()

        value = element.get('udfname')
        self.assertEqual(value, None)

        element['udfname'] = None
        value = element.get('udfname')
        self.assertEqual(value, None)

        self._assert_xml_has_value(element, "", "after setting to None")

    def test_field_is_emptystring(self):
        element = self.lims.artifacts.new()

        value = element.get('udfname')
        self.assertEqual(value, None)

        element['udfname'] = ''
        value = element.get('udfname')
        self.assertEqual(value, '')

        self._assert_xml_has_value(element, "", "after setting to empty string")

    def test_write_read_and_delete_field(self):
        # Artifact puts fields directly in the root node

        element = self.lims.artifacts.new()

        element['udfname'] = 123

        self.assertEqual(element['udfname'], 123)

        self._assert_xml_has_value(element, "123", "after setting")

        del element['udfname']

        self._assert_xml_has_value(element, "", "after deletion")

    def test_fields_in_subnode(self):

        # StepDetails puts fields in <fields>
        element = self.element_from_xml(StepDetails, STEP_DETAILS_XML, step=None)

        element['udfname'] = 123

        self.assertEqual(element['udfname'], 123)

        self._assert_xml_has_value(element, "123", "after setting (in subnode)",
                                   xpath="fields/{http://genologics.com/ri/userdefined}field")

        del element['udfname']

        self._assert_xml_has_value(element, "", "after deletion (in subnode)",
                                   xpath="fields/{http://genologics.com/ri/userdefined}field")

    def test_decimal_commas_bug(self):
        # some Clarity installs return numeric values with commas in place of decimal points due to locale setting

        test_parsed_xml = ETree.fromstring("""
<art:artifact xmlns:art="http://genologics.com/ri/artifact">
   <udf:field xmlns:udf="http://genologics.com/ri/userdefined" type="Numeric" name="udfname">0,005</udf:field>
</art:artifact>
""")

        element = Artifact(lims=self.lims, xml_root=test_parsed_xml)
        self.assertEqual(element['udfname'], 0.005)


STEP_DETAILS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<stp:details xmlns:udf="http://genologics.com/ri/userdefined" xmlns:stp="http://genologics.com/ri/step" uri="http://qalocal/api/v2/steps/24-2974/details">
    <step uri="http://qalocal/api/v2/steps/24-2974" rel="steps"/>
    <configuration uri="http://qalocal/api/v2/configuration/protocols/252/steps/554">One to One Mapping</configuration>
    <input-output-maps>
        <input-output-map>
            <input uri="http://qalocal/api/v2/artifacts/MUL101A20PA1" limsid="i1"/>
            <output uri="http://qalocal/api/v2/artifacts/2-9370" output-generation-type="PerInput" type="Analyte" limsid="o1"/>
        </input-output-map>
    </input-output-maps>
    <fields/>
</stp:details>
"""