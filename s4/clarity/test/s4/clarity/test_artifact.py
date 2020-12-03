# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
from s4.clarity.artifact import WorkflowStageHistory, Artifact, ArtifactDemux
from s4.clarity.test.generic_testcases import LimsTestCase


class TestArtifact(LimsTestCase):

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

    def test_artifact_demux_pool_of_pools(self):
        artifact_demux = self.element_from_xml(ArtifactDemux, ARTIFACT_DEMUX_POOL_OF_POOLS)

        self.assertEqual(artifact_demux.uri, "https://qalocal/api/v2/artifacts/2-1022/demux")
        self.assertEqual(artifact_demux.artifact.name, "Pool of pools")
        self.assertEqual(artifact_demux.artifact.uri, "https://qalocal/api/v2/artifacts/2-1022")
        self.assertEqual(artifact_demux.demux.pool_step.name, "Combine Pools Step Name")
        self.assertEqual(artifact_demux.demux.pool_step.uri, "https://qalocal/api/v2/steps/122-553")
        self.assertEqual(len(artifact_demux.demux.demux_artifacts), 2)

        # Sub-pool with multiple samples
        multi_sample_pool = artifact_demux.demux.demux_artifacts[1]
        # Check artifact
        self.assertEqual(multi_sample_pool.artifact.name, "Pool of multiple samples")
        self.assertEqual(multi_sample_pool.artifact.uri, "https://qalocal/api/v2/artifacts/2-1018")
        # Check samples
        self.assertEqual(len(multi_sample_pool.samples), 2)
        self.assertEqual(multi_sample_pool.samples[1].limsid, "EPP1A8")
        self.assertEqual(multi_sample_pool.samples[1].uri, "https://qalocal/api/v2/samples/EPP1A8")
        # Check reagent labels
        self.assertEqual(len(multi_sample_pool.reagent_labels), 2)
        self.assertEqual(multi_sample_pool.reagent_labels[1].name, "Reagent Label 4 (TACG-GCAT)")
        # Check demux
        self.assertEqual(multi_sample_pool.demux.pool_step.name, "Pooling Step Name")
        self.assertEqual(multi_sample_pool.demux.pool_step.uri, "https://qalocal/api/v2/steps/122-552")
        self.assertEqual(len(multi_sample_pool.demux.demux_artifacts), 2)
        self.assertEqual(multi_sample_pool.demux.demux_artifacts[0].demux, None)

        # Sub-pool with one sample
        single_sample_pool = artifact_demux.demux.demux_artifacts[0]
        self.assertEqual(single_sample_pool.artifact.name, "Pool of one sample")
        self.assertEqual(len(single_sample_pool.samples), 1)
        self.assertEqual(len(single_sample_pool.reagent_labels), 2)
        try:
            single_sample_pool.demux
            self.fail("Expected exception not thrown")
        except (AttributeError) as e:
            if (not str(e).endswith(" has no attribute 'demux'")):
                raise

    def test_artifact_demux_pool_with_primary_artifact(self):
        artifact_demux = self.element_from_xml(ArtifactDemux, ARTIFACT_DEMUX_POOL_WITH_PRIMARY_ARTIFACT)

        primary_artifact = artifact_demux.demux.demux_artifacts[1]
        self.assertEqual(primary_artifact.artifact.name, "PhiX")
        self.assertEqual(primary_artifact.artifact.uri, "https://qalocal/api/v2/artifacts/8C-54PA1")
        self.assertEqual(len(primary_artifact.samples), 0)
        self.assertEqual(len(primary_artifact.reagent_labels), 0)
        self.assertEqual(primary_artifact.demux, None)

    def test_artifact_demux_non_pooled_artifact(self):
        artifact_demux = self.element_from_xml(ArtifactDemux, ARTIFACT_DEMUX_NON_POOLED)

        self.assertEqual(artifact_demux.artifact.name, "20201027-1-6")
        self.assertEqual(artifact_demux.artifact.uri, "https://qalocal/api/v2/artifacts/2-266")
        self.assertEqual(artifact_demux.demux, None)

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

ARTIFACT_DEMUX_POOL_OF_POOLS="""
<art:demux xmlns:art="http://genologics.com/ri/artifact" uri="https://qalocal/api/v2/artifacts/2-1022/demux">
    <artifact uri="https://qalocal/api/v2/artifacts/2-1022" name="Pool of pools"/>
    <demux>
        <pool-step uri="https://qalocal/api/v2/steps/122-553" name="Combine Pools Step Name"/>
        <artifacts>
            <artifact uri="https://qalocal/api/v2/artifacts/2-1017" name="Pool of one sample">
                <samples>
                    <sample uri="https://qalocal/api/v2/samples/EPP1A6" limsid="EPP1A6"/>
                </samples>
                <reagent-labels>
                    <reagent-label name="Reagent Label 1 (ACGT-TGCA)"/>
                    <reagent-label name="Reagent Label 2 (CGTA-ATGC)"/>
                </reagent-labels>
            </artifact>
            <artifact uri="https://qalocal/api/v2/artifacts/2-1018" name="Pool of multiple samples">
                <samples>
                    <sample uri="https://qalocal/api/v2/samples/EPP1A7" limsid="EPP1A7"/>
                    <sample uri="https://qalocal/api/v2/samples/EPP1A8" limsid="EPP1A8"/>
                </samples>
                <reagent-labels>
                    <reagent-label name="Reagent Label 3 (GTAC-CATG)"/>
                    <reagent-label name="Reagent Label 4 (TACG-GCAT)"/>
                </reagent-labels>
                <demux>
                    <pool-step uri="https://qalocal/api/v2/steps/122-552" name="Pooling Step Name"/>
                    <artifacts>
                        <artifact uri="https://qalocal/api/v2/artifacts/2-621" name="20201119-1-7">
                            <samples>
                                <sample uri="https://qalocal/api/v2/samples/EPP1A7" limsid="EPP1A7"/>
                            </samples>
                            <reagent-labels>
                                <reagent-label name="Reagent Label 4 (TACG-GCAT)"/>
                            </reagent-labels>
                        </artifact>
                        <artifact uri="https://qalocal/api/v2/artifacts/2-623" name="20201119-1-8">
                            <samples>
                                <sample uri="https://qalocal/api/v2/samples/EPP1A8" limsid="EPP1A8"/>
                            </samples>
                            <reagent-labels>
                                <reagent-label name="Reagent Label 3 (GTAC-CATG)"/>
                            </reagent-labels>
                        </artifact>
                    </artifacts>
                </demux>
            </artifact>
        </artifacts>
    </demux>
</art:demux>
"""

ARTIFACT_DEMUX_POOL_WITH_PRIMARY_ARTIFACT="""
<art:demux xmlns:art="http://genologics.com/ri/artifact" uri="https://qalocal/api/v2/artifacts/2-1179/demux">
    <artifact uri="https://qalocal/api/v2/artifacts/2-1179" name="Pool #1"/>
    <demux>
        <pool-step uri="https://qalocal/api/v2/steps/122-713" name="Pooling Step Name"/>
        <artifacts>
            <artifact uri="https://qalocal/api/v2/artifacts/2-622" name="20201119-1-8">
                <samples>
                    <sample uri="https://qalocal/api/v2/samples/EPP1A8" limsid="EPP1A8"/>
                </samples>
                <reagent-labels>
                    <reagent-label name="Reagent Label 1 (ACGT-TGCA)"/>
                </reagent-labels>
            </artifact>
            <artifact uri="https://qalocal/api/v2/artifacts/8C-54PA1" name="PhiX">
                <samples/>
                <reagent-labels/>
            </artifact>
        </artifacts>
    </demux>
</art:demux>
"""

ARTIFACT_DEMUX_NON_POOLED="""
<art:demux xmlns:art="http://genologics.com/ri/artifact" uri="https://qalocal/api/v2/artifacts/2-266/demux">
    <artifact uri="https://qalocal/api/v2/artifacts/2-266" name="20201027-1-6"/>
</art:demux>
"""
