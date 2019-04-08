# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
from s4.clarity.artifact import WorkflowStageHistory, Artifact
from s4.clarity.test.generic_testcases import LimsTestCase


class TestIomaps(LimsTestCase):

    def test_workflow_stage_history(self):

        workflow_stage_history = self.element_from_xml(WorkflowStageHistory, WORKFLOW_STAGE_HISTORY_XML)

        self.assertEqual(workflow_stage_history.name, "Unit Test Stage")
        self.assertEqual(workflow_stage_history.uri, """https://qalocal/api/v2/configuration/workflows/6/stages/101""")
        self.assertEqual(workflow_stage_history.status, "COMPLETE")

        # ToDo: How do I test link nodes?
        # self.assertEqual(workflow_stage_history.stage, ?)

    def test_artifact_workflow_stages(self):

        artifact = self.element_from_xml(Artifact, ARTIFACT_WF_STAGE_XML)
        wf_stages = artifact.workflow_stages
        self.assertEqual(len(wf_stages), 3)
        self.assertEqual(wf_stages[0].name, "Stage 1")
        self.assertEqual(wf_stages[1].name, "Stage 2")
        self.assertEqual(wf_stages[2].name, "Stage 3")


    def test_artifact_multiple_samples(self):
        artifact = self.element_from_xml(Artifact, ARTIFACT_MULT_SAMPLES)
        self.assertEqual(len(artifact.samples), 2)
        self.assertEqual(artifact.samples[1].limsid,"T2")

WORKFLOW_STAGE_HISTORY_XML = """<workflow-stage status="COMPLETE" name="Unit Test Stage" uri="https://qalocal/api/v2/configuration/workflows/6/stages/101"/>"""

ARTIFACT_WF_STAGE_XML = """
<art:artifact xmlns:udf="http://genologics.com/ri/userdefined" xmlns:file="http://genologics.com/ri/file" xmlns:art="http://genologics.com/ri/artifact" uri="https://qalocal/api/v2/artifacts/ADM51A11PA1?state=178" limsid="ADM51A11PA1">
    <name>Test Artifact</name>
    <type>Analyte</type>
    <output-type>Analyte</output-type>
    <qc-flag>UNKNOWN</qc-flag>
    <location>
        <container uri="https://qalocal/api/v2/containers/27-94" limsid="27-94"/>
        <value>1:1</value>
    </location>
    <working-flag>true</working-flag>
    <sample uri="https://qalocal/api/v2/samples/ADM51A11" limsid="ADM51A11"/>
    <udf:field type="String" name="Field 1">IGHAMP</udf:field>
    <udf:field type="String" name="Field 2">IGK</udf:field>
    <udf:field type="String" name="Field 3">TRB</udf:field>
    <udf:field type="String" name="Field 4">TCRG</udf:field>
    <artifact-group name="Debug" uri="https://qalocal/api/v2/artifactgroups/51"/>
    <workflow-stages>
        <workflow-stage status="COMPLETE" name="Stage 1" uri="https://qalocal/api/v2/configuration/workflows/6/stages/101"/>
        <workflow-stage status="COMPLETE" name="Stage 2" uri="https://qalocal/api/v2/configuration/workflows/2/stages/119"/>
        <workflow-stage status="QUEUED" name="Stage 3" uri="https://qalocal/api/v2/configuration/workflows/51/stages/201"/>
    </workflow-stages>
</art:artifact>
"""

ARTIFACT_MULT_SAMPLES = """
<art:artifact xmlns:udf="http://genologics.com/ri/userdefined" xmlns:file="http://genologics.com/ri/file" xmlns:art="http://genologics.com/ri/artifact" uri="https://qalocal/api/v2/artifacts/T3?state=178" limsid="T3">
    <name>Test Artifact</name>
    <type>Analyte</type>
    <output-type>Analyte</output-type>
    <qc-flag>UNKNOWN</qc-flag>
    <location>
        <container uri="https://qalocal/api/v2/containers/27-94" limsid="27-94"/>
        <value>1:1</value>
    </location>
    <working-flag>true</working-flag>
    <sample uri="https://qalocal/api/v2/samples/T1" limsid="T1"/>
    <sample uri="https://qalocal/api/v2/samples/T2" limsid="T2"/>
</art:artifact>
"""