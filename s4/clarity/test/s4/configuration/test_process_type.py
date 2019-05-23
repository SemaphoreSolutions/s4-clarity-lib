from s4.clarity.configuration import ProcessType, ProcessTemplate
from s4.clarity.test.generic_testcases import LimsTestCase


class TestProcessType(LimsTestCase):

    def test_read_process_type_name(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(process_type.name, "Test Process")

    def test_read_process_type_attributes(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)

        def get_process_type_attribute(attribute_name):
            matching_process_attr = [a for a in process_type.process_type_attributes if a.name == attribute_name]
            self.assertEqual(len(matching_process_attr), 1)
            return matching_process_attr[0]

        self.assertEqual(get_process_type_attribute("Enabled").value, 'true')
        self.assertEqual(get_process_type_attribute("Family").value, 'Configured')
        self.assertEqual(get_process_type_attribute("ContextCode").value, 'DNA')
        self.assertEqual(get_process_type_attribute("SkipInputPanel").value, 'false')
        self.assertEqual(get_process_type_attribute("VolumeAdjustmentType").value, 'None')

    def test_read_process_type_inputs(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(process_type.input.artifact_type, 'Analyte')
        self.assertEqual(process_type.input.display_name, 'Analyte')
        self.assertEqual(process_type.input.remove_working_flag, False)

    def test_read_process_type_outputs(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(len(process_type.outputs), 2)

        first_output = process_type.outputs[0]
        self.assertEqual(first_output.artifact_type, 'Analyte')
        self.assertEqual(first_output.display_name, 'Analyte')
        self.assertEqual(first_output.output_generation_type, 'PerInput')
        self.assertEqual(first_output.number_of_outputs, 1)
        self.assertEqual(first_output.output_name, '{InputItemName}')
        self.assertEqual(first_output.assign_working_flag, False)

        self.assertEqual(len(first_output.field_definitions), 2)
        self.assertEqual(first_output.field_definitions[0].name, 'Analite UDF 3')

    def test_read_process_type_parameters(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(len(process_type.parameters), 2)

        first_paramater = process_type.parameters[0]
        self.assertEqual(first_paramater.name, 'First Automation')
        self.assertEqual(first_paramater.command_string, 'SCRIPT_BODY_1')
        self.assertEqual(first_paramater.run_program_per_event, False)
        self.assertEqual(first_paramater.channel, 'limsserver')
        self.assertEqual(first_paramater.invocation_type, 'PostProcess')

    def test_read_process_type_fields(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(len(process_type.field_definitions), 2)
        self.assertEqual(process_type.field_definitions[0].name, 'Step UDF 1')


    def test_read_permitted_containers(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(len(process_type.permitted_containers), 1)

        permitted_container = process_type.permitted_containers[0]
        self.assertEqual(permitted_container.name, '96 well plate')

    def test_required_reagent_kits(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(len(process_type.required_reagent_kits), 4)
        self.assertEqual(process_type.required_reagent_kits[0].name, 'Kit 1')
        self.assertEqual(process_type.required_reagent_kits[0].uri, 'https://qalocal/api/v2/reagentkits/1')

    def test_permitted_instrument_types(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(len(process_type.permitted_instrument_types), 1)
        self.assertEqual(process_type.permitted_instrument_types[0].instrument_type, 'Instrument 1')

    def test_read_queue_fields(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(len(process_type.queue_fields), 3)
        self.assertEqual(process_type.queue_fields[0].detail, 'false')
        self.assertEqual(process_type.queue_fields[0].style, 'USER_DEFINED')
        self.assertEqual(process_type.queue_fields[0].attach_to, 'Analyte')
        self.assertEqual(process_type.queue_fields[0].name, 'Analite UDF 1')


    def test_read_ice_bucket_fields(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(len(process_type.ice_bucket_fields), 2)
        self.assertEqual(process_type.ice_bucket_fields[0].detail, 'false')
        self.assertEqual(process_type.ice_bucket_fields[0].style, 'USER_DEFINED')
        self.assertEqual(process_type.ice_bucket_fields[0].attach_to, 'Analyte')
        self.assertEqual(process_type.ice_bucket_fields[0].name, 'Analite UDF 1')

    def test_read_step_fields(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(len(process_type.step_fields), 2)
        self.assertEqual(process_type.step_fields[0].style, 'USER_DEFINED')
        self.assertEqual(process_type.step_fields[0].attach_to, 'ConfiguredProcess')
        self.assertEqual(process_type.step_fields[0].name, 'step udf 1')

    def test_read_sample_fields(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(len(process_type.sample_fields), 2)

        first_sample_field = process_type.sample_fields[0]
        self.assertEqual(first_sample_field.name, 'Analite UDF 3')
        self.assertEqual(first_sample_field.attach_to, 'Analyte')
        self.assertEqual(first_sample_field.style, 'USER_DEFINED')

    def test_read_step_properties(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(len(process_type.step_properties), 3)
        self.assertEqual(process_type.step_properties[0].name, 'prop1')
        self.assertEqual(process_type.step_properties[0].value, 'val 1')
        self.assertEqual(process_type.step_properties[2].name, 'prop3')
        self.assertEqual(process_type.step_properties[2].value, 'val 3')

    def test_read_epp_triggers(self):
        process_type = self.element_from_xml(ProcessType, TEST_PROCESS_XML)
        self.assertEqual(len(process_type.epp_triggers), 2)
        self.assertEqual(process_type.epp_triggers[0].type, 'AUTOMATIC')
        self.assertEqual(process_type.epp_triggers[0].name, 'End of Step')
        self.assertEqual(process_type.epp_triggers[0].point, 'BEFORE')
        self.assertEqual(process_type.epp_triggers[0].status, 'COMPLETE')


class TestProcessTemplate(LimsTestCase):
    def test_read_process_template(self):
        process_template = self.element_from_xml(ProcessTemplate, TEST_PROCESS_TEMPLATE_XML)
        self.assertEqual(process_template.uri, 'https://qalocal/api/v2/processtemplates/2')
        self.assertEqual(process_template.name, 'Process Template Name')
        self.assertEqual(process_template.technician.uri, 'https://qalocal/api/v2/researchers/3')

        self.assertEqual(process_template["Field 1"], 'Field 1 Value')
        self.assertEqual(process_template["Field 2"], 'Field 2 Value')



####################
# XML Blobs
####################


TEST_PROCESS_XML = """
<ptp:process-type xmlns:file="http://genologics.com/ri/file" xmlns:ptp="http://genologics.com/ri/processtype" uri="https://qalocal/api/v2/processtypes/1" name="Test Process">
    <field-definition uri="https://qalocal/api/v2/configuration/udfs/1" name="Step UDF 1"/>
    <field-definition uri="https://qalocal/api/v2/configuration/udfs/2" name="Step UDF 2"/>

    <parameter uri="https://qalocal/api/v2/configuration/automations/1" name="First Automation">
        <string>SCRIPT_BODY_1</string>
        <run-program-per-event>false</run-program-per-event>
        <channel>limsserver</channel>
        <invocation-type>PostProcess</invocation-type>
    </parameter>
    <parameter uri="https://qalocal/api/v2/configuration/automations/2" name="Second Automation">
        <string>script body 2</string>
        <run-program-per-event>false</run-program-per-event>
        <channel>limsserver</channel>
        <invocation-type>PostProcess</invocation-type>
    </parameter>

    <process-input>
        <artifact-type>Analyte</artifact-type>
        <display-name>Analyte</display-name>
        <remove-working-flag>false</remove-working-flag>
    </process-input>

    <process-output>
        <artifact-type>Analyte</artifact-type>
        <display-name>Analyte</display-name>
        <output-generation-type>PerInput</output-generation-type>
        <variability-type>Fixed</variability-type>
        <number-of-outputs>1</number-of-outputs>
        <output-name>{InputItemName}</output-name>
        <field-definition uri="https://qalocal/api/v2/configuration/udfs/3" name="Analite UDF 3"/>
        <field-definition uri="https://qalocal/api/v2/configuration/udfs/4" name="Analite UDF 4"/>
        <assign-working-flag>false</assign-working-flag>
    </process-output>

    <process-output>
        <artifact-type>ResultFile</artifact-type>
        <display-name>ResultFile</display-name>
        <output-generation-type>PerAllInputs</output-generation-type>
        <variability-type>Fixed</variability-type>
        <number-of-outputs>1</number-of-outputs>
        <output-name>Result File 1</output-name>
    </process-output>

    <process-type-attribute name="Enabled">true</process-type-attribute>
    <process-type-attribute name="Family">Configured</process-type-attribute>
    <process-type-attribute name="ContextCode">DNA</process-type-attribute>
    <process-type-attribute name="OutputContextCode">DN</process-type-attribute>
    <process-type-attribute name="ConsumeVolume">true</process-type-attribute>
    <process-type-attribute name="InheritsQC">false</process-type-attribute>
    <process-type-attribute name="ModifyInputOutput">All</process-type-attribute>
    <process-type-attribute name="OnlyEnableDoneAtLastPanel">false</process-type-attribute>
    <process-type-attribute name="OutputSorting">Input LIMS ID</process-type-attribute>
    <process-type-attribute name="ProcessGroup">Configured Processes</process-type-attribute>
    <process-type-attribute name="ProcessTabView">Use the default display</process-type-attribute>
    <process-type-attribute name="QCAdjustmentType">None</process-type-attribute>
    <process-type-attribute name="SkipInputPanel">false</process-type-attribute>
    <process-type-attribute name="VolumeAdjustmentType">None</process-type-attribute>

    <permitted-containers>
        <container-type uri="https://qalocal/api/v2/containertypes/1" name="96 well plate"/>
    </permitted-containers>

    <permitted-reagent-categories/>

    <required-reagent-kits>
        <reagent-kit uri="https://qalocal/api/v2/reagentkits/1" name="Kit 1"/>
        <reagent-kit uri="https://qalocal/api/v2/reagentkits/2" name="Kit 2"/>
        <reagent-kit uri="https://qalocal/api/v2/reagentkits/3" name="Kit 3"/>
        <reagent-kit uri="https://qalocal/api/v2/reagentkits/4" name="Kit 4"/>
    </required-reagent-kits>

    <permitted-control-types/>

    <permitted-instrument-types>
        <instrument-type>Instrument 1</instrument-type>
    </permitted-instrument-types>

    <queue-fields>
        <queue-field detail="false" style="USER_DEFINED" attach-to="Analyte" name="Analite UDF 1"/>
        <queue-field detail="true" style="USER_DEFINED" attach-to="Analyte" name="Analite UDF 2"/>
        <queue-field detail="true" style="BUILT_IN" attach-to="Analyte" name="Waiting"/>
    </queue-fields>

    <ice-bucket-fields>
        <ice-bucket-field detail="false" style="USER_DEFINED" attach-to="Analyte" name="Analite UDF 1"/>
        <ice-bucket-field detail="true" style="USER_DEFINED" attach-to="Analyte" name="Analite UDF 2"/>
    </ice-bucket-fields>

    <step-fields>
        <step-field style="USER_DEFINED" attach-to="ConfiguredProcess" name="step udf 1"/>
        <step-field style="USER_DEFINED" attach-to="ConfiguredProcess" name="step udf 2"/>
    </step-fields>

    <sample-fields>
        <sample-field style="USER_DEFINED" attach-to="Analyte" name="Analite UDF 3"/>
        <sample-field style="USER_DEFINED" attach-to="Analyte" name="Anilite UDF 4"/>
    </sample-fields>

    <step-properties>
        <step-property value="val 1" name="prop1"/>
        <step-property value="val 2" name="prop2"/>
        <step-property value="val 3" name="prop3"/>
    </step-properties>

    <epp-triggers>
        <epp-trigger status="COMPLETE" point="BEFORE" type="AUTOMATIC" name="End of Step"/>
        <epp-trigger status="PLACEMENT" point="BEFORE" type="AUTOMATIC" name="Placement Enter"/>
    </epp-triggers>

</ptp:process-type>
"""

TEST_PROCESS_TEMPLATE_XML = """
<ptm:process-template xmlns:udf="http://genologics.com/ri/userdefined" xmlns:ptm="http://genologics.com/ri/processtemplate" uri="https://qalocal/api/v2/processtemplates/2">
    <name>Process Template Name</name>
    <type uri="https://qalocal/api/v2/processtypes/2">Second Process</type>

    <technician uri="https://qalocal/api/v2/researchers/3">
        <first-name>API</first-name>
        <last-name>Access</last-name>
    </technician>

    <udf:field type="String" name="Field 1">Field 1 Value</udf:field>
    <udf:field type="String" name="Field 2">Field 2 Value</udf:field>

    <is-default>false</is-default>
</ptm:process-template>
"""